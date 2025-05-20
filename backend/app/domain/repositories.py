from abc import ABC, abstractmethod
from typing import Optional, List, BinaryIO, Optional
from domain.entities import File, Folder, User
from fastapi import UploadFile


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


class FileStorageRepository(ABC):
    @abstractmethod
    async def save(self, file: UploadFile, filename: str) -> str:
        pass
    
    @abstractmethod
    async def get(self, filename: str) -> Optional[BinaryIO]:
        pass
    
    @abstractmethod
    async def delete(self, filename: str) -> bool:
        pass


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


class UserRepository(ABC):
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def update(self, user_id: str, data: dict) -> Optional[User]:
        pass
