from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime

class FileResponse(BaseModel):
    id: str
    filename: str
    original_filename: str
    content_type: str
    size: int
    owner_id: str
    parent_folder_id: Optional[str] = None
    shared_with: List[str] = []
    is_public: bool
    public_link: Optional[str] = None
    public_link_expiry: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class ShareFileRequest(BaseModel):
    user_id: str

class CreatePublicLinkRequest(BaseModel):
    expires_in_days: Optional[int] = None

class PublicLinkResponse(BaseModel):
    public_link: str
    expires_at: Optional[datetime] = None

class FolderRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    parent_folder_id: Optional[str] = None

class FolderResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    parent_folder_id: Optional[str] = None
    shared_with: List[str] = []
    created_at: datetime
    updated_at: datetime

class UserRegistrationRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"