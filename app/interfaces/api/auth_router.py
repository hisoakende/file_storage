from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from ...domain.use_cases.user_use_cases import UserUseCases
from ..serializers.user_serializers import UserRegistrationRequest, UserLoginRequest, UserResponse, TokenResponse
from ...domain.entities.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_use_cases: UserUseCases = Depends()
) -> User:
    user = await user_use_cases.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegistrationRequest,
    user_use_cases: UserUseCases = Depends()
):
    try:
        user = await user_use_cases.register_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        return {
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_use_cases: UserUseCases = Depends()
):
    token = await user_use_cases.authenticate_user(
        email=form_data.username,  # OAuth2 form uses 'username' field
        password=form_data.password
    )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }
