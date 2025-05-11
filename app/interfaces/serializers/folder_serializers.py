from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

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
