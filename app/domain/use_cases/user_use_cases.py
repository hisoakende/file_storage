from ..entities.user import User
from ..repositories.user_repository import UserRepository
from typing import Optional
import bcrypt
from datetime import datetime, timedelta
import jwt
from jwt.exceptions import InvalidTokenError

class UserUseCases:
    def __init__(self, user_repository: UserRepository, secret_key: str):
        self.user_repository = user_repository
        self.secret_key = secret_key
    
    async def register_user(self, username: str, email: str, password: str) -> User:
        # Check if user exists
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        existing_username = await self.user_repository.get_by_username(username)
        if existing_username:
            raise ValueError("Username is already taken")
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        return await self.user_repository.create(user)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[str]:
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return None
        
        # Generate JWT token
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(days=1)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
    
    async def get_user_from_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload.get("sub")
            if not user_id:
                return None
            
            return await self.user_repository.get_by_id(user_id)
        except InvalidTokenError:
            return None
