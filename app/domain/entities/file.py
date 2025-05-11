from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from .base import PyObjectId

class File(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    filename: str
    original_filename: str
    content_type: str
    size: int
    owner_id: PyObjectId
    parent_folder_id: Optional[PyObjectId] = None
    shared_with: List[PyObjectId] = []
    is_public: bool = False
    public_link: Optional[str] = None
    public_link_expiry: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

