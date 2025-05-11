from motor.motor_asyncio import AsyncIOMotorCollection
from ...domain.repositories.folder_repository import FolderRepository
from ...domain.entities.folder import Folder
from typing import Optional, List
from bson import ObjectId
from datetime import datetime

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
