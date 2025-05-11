from motor.motor_asyncio import AsyncIOMotorCollection
from ...domain.repositories.user_repository import UserRepository
from ...domain.entities.user import User
from typing import Optional, List
from bson import ObjectId

class MongoDBUserRepository(UserRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create(self, user: User) -> User:
        user_dict = user.dict(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(user_dict)
        user_dict["_id"] = result.inserted_id
        return User(**user_dict)
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        user_dict = await self.collection.find_one({"_id": ObjectId(user_id)})
        if user_dict:
            return User(**user_dict)
        return None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        user_dict = await self.collection.find_one({"email": email})
        if user_dict:
            return User(**user_dict)
        return None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        user_dict = await self.collection.find_one({"username": username})
        if user_dict:
            return User(**user_dict)
        return None
    
    async def update(self, user_id: str, data: dict) -> Optional[User]:
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data}
        )
        if result.modified_count:
            return await self.get_by_id(user_id)
        return None
