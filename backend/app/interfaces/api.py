from typing import Optional, List
from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    status, 
    UploadFile
)
from fastapi import File as FastAPIFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import bcrypt

from domain.entities import User, File, Folder
from domain.use_cases import UserUseCases, FileUseCases, FolderUseCases
from dependencies import get_user_use_cases, get_file_use_cases, get_folder_use_cases

from interfaces.serializers import (
    UserRegistrationRequest,
    ShareFileRequest,
    CreatePublicLinkRequest,
    FolderRequest,
    UserResponse,
    TokenResponse,
    FileResponse,
    FolderResponse,
    PublicLinkResponse
)

router = APIRouter(prefix="/api")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
) -> User:
    user = await user_use_cases.get_user_from_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegistrationRequest,
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
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

@router.post("/auth/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_use_cases: UserUseCases = Depends(get_user_use_cases)
):
    token = await user_use_cases.authenticate_user(
        email=form_data.username,
        password=form_data.password
    )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"access_token": token, "token_type": "bearer"}

@router.get("/auth/me", response_model=UserResponse)
async def get_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "username": current_user.username,
        "email": current_user.email,
        "created_at": current_user.created_at
    }


@router.post("/files/", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends(get_file_use_cases)
):
    uploaded_file = await file_use_cases.upload_file(
        upload_file=file,
        owner_id=str(current_user.id),
        parent_folder_id=folder_id
    )
    
    return {
        "id": str(uploaded_file.id),
        "filename": uploaded_file.filename,
        "original_filename": uploaded_file.original_filename,
        "content_type": uploaded_file.content_type,
        "size": uploaded_file.size,
        "owner_id": str(uploaded_file.owner_id),
        "parent_folder_id": str(uploaded_file.parent_folder_id) if uploaded_file.parent_folder_id else None,
        "shared_with": [str(user_id) for user_id in uploaded_file.shared_with],
        "is_public": uploaded_file.is_public,
        "public_link": uploaded_file.public_link,
        "public_link_expiry": uploaded_file.public_link_expiry,
        "created_at": uploaded_file.created_at,
        "updated_at": uploaded_file.updated_at
    }

@router.get("/files/", response_model=List[FileResponse])
async def list_files(
    folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends(get_file_use_cases)
):
    files = await file_use_cases.list_files(
        owner_id=str(current_user.id),
        folder_id=folder_id
    )
    
    return [
        {
            "id": str(file.id),
            "filename": file.filename,
            "original_filename": file.original_filename,
            "content_type": file.content_type,
            "size": file.size,
            "owner_id": str(file.owner_id),
            "parent_folder_id": str(file.parent_folder_id) if file.parent_folder_id else None,
            "shared_with": [str(user_id) for user_id in file.shared_with],
            "is_public": file.is_public,
            "public_link": file.public_link,
            "public_link_expiry": file.public_link_expiry,
            "created_at": file.created_at,
            "updated_at": file.updated_at
        }
        for file in files
    ]

@router.get("/files/shared", response_model=List[FileResponse])
async def list_shared_files(
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends(get_file_use_cases)
):
    files = await file_use_cases.list_shared_files(user_id=str(current_user.id))
    
    return [
        {
            "id": str(file.id),
            "filename": file.filename,
            "original_filename": file.original_filename,
            "content_type": file.content_type,
            "size": file.size,
            "owner_id": str(file.owner_id),
            "parent_folder_id": str(file.parent_folder_id) if file.parent_folder_id else None,
            "shared_with": [str(user_id) for user_id in file.shared_with],
            "is_public": file.is_public,
            "public_link": file.public_link,
            "public_link_expiry": file.public_link_expiry,
            "created_at": file.created_at,
            "updated_at": file.updated_at
        }
        for file in files
    ]

@router.get("/files/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends(get_file_use_cases)
):
    file_tuple = await file_use_cases.download_file(file_id, str(current_user.id))
    if not file_tuple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to it"
        )
    file, _, _ = file_tuple
    file_details = await file_use_cases.file_repository.get_by_id(file_id)
    return {
        "id": str(file_details.id),
        "filename": file_details.filename,
        "original_filename": file_details.original_filename,
        "content_type": file_details.content_type,
        "size": file_details.size,
        "owner_id": str(file_details.owner_id),
        "parent_folder_id": str(file_details.parent_folder_id) if file_details.parent_folder_id else None,
        "shared_with": [str(user_id) for user_id in file_details.shared_with],
        "is_public": file_details.is_public,
        "public_link": file_details.public_link,
        "public_link_expiry": file_details.public_link_expiry,
        "created_at": file_details.created_at,
        "updated_at": file_details.updated_at
    }

@router.get("/files/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends(get_file_use_cases)
):
    file_tuple = await file_use_cases.download_file(file_id, str(current_user.id))
    if not file_tuple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to it"
        )
    file_content, original_filename, content_type = file_tuple
    return StreamingResponse(
        content=file_content,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename=\"{original_filename}\""}
    )

@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends(get_file_use_cases)
):
    deleted = await file_use_cases.delete_file(file_id, str(current_user.id))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to delete it"
        )

@router.post("/files/{file_id}/share", response_model=FileResponse)
async def share_file(
    file_id: str,
    share_data: ShareFileRequest,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends(get_file_use_cases)
):
    shared_file = await file_use_cases.share_file(
        file_id=file_id,
        owner_id=str(current_user.id),
        shared_with_id=share_data.user_id
    )
    if not shared_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to share it"
        )
    return {
        "id": str(shared_file.id),
        "filename": shared_file.filename,
        "original_filename": shared_file.original_filename,
        "content_type": shared_file.content_type,
        "size": shared_file.size,
        "owner_id": str(shared_file.owner_id),
        "parent_folder_id": str(shared_file.parent_folder_id) if shared_file.parent_folder_id else None,
        "shared_with": [str(user_id) for user_id in shared_file.shared_with],
        "is_public": shared_file.is_public,
        "public_link": shared_file.public_link,
        "public_link_expiry": shared_file.public_link_expiry,
        "created_at": shared_file.created_at,
        "updated_at": shared_file.updated_at
    }

@router.post("/files/{file_id}/public-link", response_model=PublicLinkResponse)
async def create_public_link(
    file_id: str,
    link_data: CreatePublicLinkRequest,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends(get_file_use_cases)
):
    public_link = await file_use_cases.create_public_link(
        file_id=file_id,
        owner_id=str(current_user.id),
        expires_in_days=link_data.expires_in_days
    )
    if not public_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to create a public link"
        )
    file = await file_use_cases.file_repository.get_by_id(file_id)
    return {
        "public_link": public_link,
        "expires_at": file.public_link_expiry
    }

@router.get("/files/public/{public_key}")
async def access_public_file(
    public_key: str,
    file_use_cases: FileUseCases = Depends(get_file_use_cases)
):
    public_link = f"/api/files/public/{public_key}"
    file = await file_use_cases.get_file_by_public_link(public_link)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public file not found or link has expired"
        )
    file_content = await file_use_cases.file_storage_repository.get(file.filename)
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File content not found"
        )
    return StreamingResponse(
        content=file_content,
        media_type=file.content_type,
        headers={"Content-Disposition": f"attachment; filename=\"{file.original_filename}\""}
    )

@router.post("/folders/", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_data: FolderRequest,
    current_user: User = Depends(get_current_user),
    folder_use_cases: FolderUseCases = Depends(get_folder_use_cases)
):
    folder = await folder_use_cases.create_folder(
        name=folder_data.name,
        owner_id=str(current_user.id),
        parent_folder_id=folder_data.parent_folder_id
    )
    
    return {
        "id": str(folder.id),
        "name": folder.name,
        "owner_id": str(folder.owner_id),
        "parent_folder_id": str(folder.parent_folder_id) if folder.parent_folder_id else None,
        "shared_with": [str(user_id) for user_id in folder.shared_with],
        "created_at": folder.created_at,
        "updated_at": folder.updated_at
    }

@router.get("/folders/", response_model=List[FolderResponse])
async def list_folders(
    parent_folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    folder_use_cases: FolderUseCases = Depends(get_folder_use_cases)
):
    folders = await folder_use_cases.list_folders(
        owner_id=str(current_user.id),
        parent_folder_id=parent_folder_id
    )
    return [
        {
            "id": str(folder.id),
            "name": folder.name,
            "owner_id": str(folder.owner_id),
            "parent_folder_id": str(folder.parent_folder_id) if folder.parent_folder_id else None,
            "shared_with": [str(user_id) for user_id in folder.shared_with],
            "created_at": folder.created_at,
            "updated_at": folder.updated_at
        }
        for folder in folders
    ]

@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: str,
    current_user: User = Depends(get_current_user),
    folder_use_cases: FolderUseCases = Depends(get_folder_use_cases)
):
    deleted = await folder_use_cases.delete_folder(folder_id, str(current_user.id))
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found or you don't have access to delete it"
        )

@router.post("/folders/{folder_id}/share", response_model=FolderResponse)
async def share_folder(
    folder_id: str,
    share_data: ShareFileRequest,
    current_user: User = Depends(get_current_user),
    folder_use_cases: FolderUseCases = Depends(get_folder_use_cases)
):
    shared_folder = await folder_use_cases.share_folder(
        folder_id=folder_id,
        owner_id=str(current_user.id),
        shared_with_id=share_data.user_id
    )
    if not shared_folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found or you don't have access to share it"
        )
    return {
        "id": str(shared_folder.id),
        "name": shared_folder.name,
        "owner_id": str(shared_folder.owner_id),
        "parent_folder_id": str(shared_folder.parent_folder_id) if shared_folder.parent_folder_id else None,
        "shared_with": [str(user_id) for user_id in shared_folder.shared_with],
        "created_at": shared_folder.created_at,
        "updated_at": shared_folder.updated_at
    }
