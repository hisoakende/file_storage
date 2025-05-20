from datetime import datetime
from typing import Any, Annotated, Optional, List
from bson import ObjectId
from pydantic import BaseModel, Field, BeforeValidator, PlainSerializer, ConfigDict, EmailStr
from pydantic_mongo import ObjectIdField


def validate_object_id(v: Any) -> Optional[ObjectId]:
    if v is None:
        return None
    if isinstance(v, ObjectId):
        return v
    if isinstance(v, str) and ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError(f"Invalid ObjectId: {v}")


PyObjectId = Annotated[
    str,
    BeforeValidator(validate_object_id),
    PlainSerializer(lambda x: str(x) if x else None, return_type=str)
]


class MongoBaseModel(BaseModel):
    id: Optional[ObjectIdField] = Field(default=None, alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
    
    def mongo_dict(self) -> dict[str, Any]:
        data = self.model_dump(by_alias=True, exclude_none=True)
        if "_id" in data and data["_id"] is None:
            del data["_id"]
        return data
    
    @classmethod
    def from_mongo(cls, data: dict[str, Any]):
        if data is None:
            return None
        return cls.model_validate(data)


class File(MongoBaseModel):
    filename: str
    original_filename: str
    content_type: str
    size: int
    owner_id: ObjectIdField
    parent_folder_id: Optional[ObjectIdField] = None
    shared_with: List[ObjectIdField] = []
    is_public: bool = False
    public_link: Optional[str] = None
    public_link_expiry: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "json_encoders": {ObjectId: str}
        }
    
    def model_dump(self, **kwargs):
        kwargs.pop("exclude_none", None)
        data = super().model_dump(**kwargs)
        if data.get("_id") is not None:
            data["_id"] = str(data["_id"])
        return data


class Folder(MongoBaseModel):
    name: str
    owner_id: ObjectIdField
    parent_folder_id: Optional[ObjectIdField] = None
    shared_with: List[ObjectIdField] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "json_encoders": {ObjectId: str}
        }

    def model_dump(self, **kwargs):
        kwargs.pop("exclude_none", None)
        data = super().model_dump(**kwargs)
        if data.get("_id") is not None:
            data["_id"] = str(data["_id"])
        return data


class User(MongoBaseModel):
    username: str
    email: EmailStr
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "json_encoders": {ObjectId: str}
        }

    def model_dump(self, **kwargs):
        kwargs.pop("exclude_none", None)
        data = super().model_dump(**kwargs)
        if data.get("_id") is not None:
            data["_id"] = str(data["_id"])
        return data
