from typing import Optional, List
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from domain.entities import File, Folder, User
from domain.repositories import FolderRepository, FileRepository, UserRepository, FileStorageRepository

class MongoDBUserRepository(UserRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create(self, user: User) -> User:
        user_dict = user.mongo_dict()
        result = await self.collection.insert_one(user_dict)
        created_user = await self.collection.find_one({"_id": result.inserted_id})
        return User.from_mongo(created_user)
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        user_dict = await self.collection.find_one({"_id": ObjectId(user_id)})
        return User.from_mongo(user_dict)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        user_dict = await self.collection.find_one({"email": email})
        return User.from_mongo(user_dict)
    
    async def get_by_username(self, username: str) -> Optional[User]:
        user_dict = await self.collection.find_one({"username": username})
        return User.from_mongo(user_dict)
    
    async def update(self, user_id: str, data: dict) -> Optional[User]:
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data}
        )
        if result.modified_count:
            return await self.get_by_id(user_id)
        return None

class MongoDBFolderRepository(FolderRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create(self, folder: Folder) -> Folder:
        folder_dict = folder.dict(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(folder_dict)
        folder_dict["_id"] = result.inserted_id
        return Folder(**folder_dict)
    
    async def get_by_id(self, folder_id: str) -> Optional[Folder]:
        folder_dict = await self.collection.find_one({"_id": ObjectId(folder_id)})
        if folder_dict:
            return Folder(**folder_dict)
        return None
    
    async def list_by_owner(self, owner_id: str, parent_folder_id: Optional[str] = None) -> List[Folder]:
        query = {"owner_id": ObjectId(owner_id)}
        if parent_folder_id:
            query["parent_folder_id"] = ObjectId(parent_folder_id)
        else:
            query["parent_folder_id"] = None
        
        folders = []
        async for folder_dict in self.collection.find(query):
            folders.append(Folder(**folder_dict))
        return folders
    
    async def update(self, folder_id: str, data: dict) -> Optional[Folder]:
        data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(folder_id)},
            {"$set": data}
        )
        if result.modified_count:
            return await self.get_by_id(folder_id)
        return None
    
    async def delete(self, folder_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(folder_id)})
        return result.deleted_count > 0

class MongoDBFileRepository(FileRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def create(self, file: File) -> File:
        file_dict = file.dict(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(file_dict)
        file_dict["_id"] = result.inserted_id
        return File(**file_dict)
    
    async def get_by_id(self, file_id: str) -> Optional[File]:
        file_dict = await self.collection.find_one({"_id": ObjectId(file_id)})
        if file_dict:
            return File(**file_dict)
        return None
    
    async def list_by_owner(self, owner_id: str, folder_id: Optional[str] = None) -> List[File]:
        query = {"owner_id": ObjectId(owner_id)}
        if folder_id:
            query["parent_folder_id"] = ObjectId(folder_id)
        else:
            query["parent_folder_id"] = None
        
        files = []
        async for file_dict in self.collection.find(query):
            files.append(File(**file_dict))
        return files
    
    async def list_shared_with_user(self, user_id: str) -> List[File]:
        query = {"shared_with": ObjectId(user_id)}
        files = []
        async for file_dict in self.collection.find(query):
            files.append(File(**file_dict))
        return files
    
    async def list_public_by_link(self, public_link: str) -> List[File]:
        query = {"public_link": public_link, "is_public": True}
        files = []
        async for file_dict in self.collection.find(query):
            files.append(File(**file_dict))
        return files
    
    async def update(self, file_id: str, data: dict) -> Optional[File]:
        data["updated_at"] = datetime.utcnow()
        result = await self.collection.update_one(
            {"_id": ObjectId(file_id)},
            {"$set": data}
        )
        if result.modified_count:
            return await self.get_by_id(file_id)
        return None
    
    async def delete(self, file_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(file_id)})
        return result.deleted_count > 0
