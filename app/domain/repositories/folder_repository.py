from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.folder import Folder

class FolderRepository(ABC):
    @abstractmethod
    async def create(self, folder: Folder) -> Folder:
        pass
    
    @abstractmethod
    async def get_by_id(self, folder_id: str) -> Optional[Folder]:
        pass
    
    @abstractmethod
    async def list_by_owner(self, owner_id: str, parent_folder_id: Optional[str] = None) -> List[Folder]:
        pass
    
    @abstractmethod
    async def update(self, folder_id: str, data: dict) -> Optional[Folder]:
        pass
    
    @abstractmethod
    async def delete(self, folder_id: str) -> bool:
        pass
