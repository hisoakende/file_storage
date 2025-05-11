from abc import ABC, abstractmethod
from typing import Optional, List
from ..entities.file import File

class FileRepository(ABC):
    @abstractmethod
    async def create(self, file: File) -> File:
        pass
    
    @abstractmethod
    async def get_by_id(self, file_id: str) -> Optional[File]:
        pass
    
    @abstractmethod
    async def list_by_owner(self, owner_id: str, folder_id: Optional[str] = None) -> List[File]:
        pass
    
    @abstractmethod
    async def list_shared_with_user(self, user_id: str) -> List[File]:
        pass
    
    @abstractmethod
    async def update(self, file_id: str, data: dict) -> Optional[File]:
        pass
    
    @abstractmethod
    async def delete(self, file_id: str) -> bool:
        pass
