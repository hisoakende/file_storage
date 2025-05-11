from pydantic import BaseModel, Field
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
