from ...domain.repositories.file_storage_repository import FileStorageRepository
from typing import BinaryIO, Optional
from fastapi import UploadFile
import os
import shutil
import aiofiles

class LocalFileStorageRepository(FileStorageRepository):
    def __init__(self, storage_path: str):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
    
    async def save(self, file: UploadFile, filename: str) -> str:
        file_path = os.path.join(self.storage_path, filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            # Reset file position
            await file.seek(0)
            
            # Read and write in chunks
            content = await file.read()
            await out_file.write(content)
        
        return filename
    
    async def get(self, filename: str) -> Optional[BinaryIO]:
        file_path = os.path.join(self.storage_path, filename)
        if not os.path.exists(file_path):
            return None
        
        return open(file_path, 'rb')
    
    async def delete(self, filename: str) -> bool:
        file_path = os.path.join(self.storage_path, filename)
        if not os.path.exists(file_path):
            return False
        
        os.remove(file_path)
        return True
