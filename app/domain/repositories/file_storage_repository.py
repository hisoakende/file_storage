from abc import ABC, abstractmethod
from typing import BinaryIO, Optional
from fastapi import UploadFile

class FileStorageRepository(ABC):
    @abstractmethod
    async def save(self, file: UploadFile, filename: str) -> str:
        """Save file to storage and return path/identifier"""
        pass
    
    @abstractmethod
    async def get(self, filename: str) -> Optional[BinaryIO]:
        """Get file from storage by path/identifier"""
        pass
    
    @abstractmethod
    async def delete(self, filename: str) -> bool:
        """Delete file from storage"""
        pass
