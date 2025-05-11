from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from .base import PyObjectId

class Folder(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    owner_id: PyObjectId
    parent_folder_id: Optional[PyObjectId] = None
    shared_with: List[PyObjectId] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
