from ..entities.folder import Folder
from ..repositories.folder_repository import FolderRepository
from ..repositories.file_repository import FileRepository
from typing import Optional, List
from bson import ObjectId

class FolderUseCases:
    def __init__(
        self, 
        folder_repository: FolderRepository,
        file_repository: FileRepository
    ):
        self.folder_repository = folder_repository
        self.file_repository = file_repository
    
    async def create_folder(
        self, 
        name: str, 
        owner_id: str,
        parent_folder_id: Optional[str] = None
    ) -> Folder:
        folder = Folder(
            name=name,
            owner_id=ObjectId(owner_id),
            parent_folder_id=ObjectId(parent_folder_id) if parent_folder_id else None
        )
        
        return await self.folder_repository.create(folder)
    
    async def list_folders(self, owner_id: str, parent_folder_id: Optional[str] = None) -> List[Folder]:
        return await self.folder_repository.list_by_owner(owner_id, parent_folder_id)
    
    async def delete_folder(self, folder_id: str, owner_id: str) -> bool:
        # Get folder
        folder = await self.folder_repository.get_by_id(folder_id)
        if not folder:
            return False
        
        # Check if user is owner
        if str(folder.owner_id) != owner_id:
            return False
        
        # Delete all files in folder
        files = await self.file_repository.list_by_owner(owner_id, folder_id)
        for file in files:
            await self.file_repository.delete(str(file.id))
        
        # Delete all subfolders recursively
        subfolders = await self.folder_repository.list_by_owner(owner_id, folder_id)
        for subfolder in subfolders:
            await self.delete_folder(str(subfolder.id), owner_id)
        
        # Delete folder
        return await self.folder_repository.delete(folder_id)
    
    async def share_folder(self, folder_id: str, owner_id: str, shared_with_id: str) -> Optional[Folder]:
        # Get folder
        folder = await self.folder_repository.get_by_id(folder_id)
        if not folder:
            return None
        
        # Check if user is owner
        if str(folder.owner_id) != owner_id:
            return None
        
        # Add user to shared_with list if not already there
        if ObjectId(shared_with_id) not in folder.shared_with:
            folder.shared_with.append(ObjectId(shared_with_id))
            return await self.folder_repository.update(folder_id, {"shared_with": folder.shared_with})
        
        return folder
