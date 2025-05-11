from ..entities.file import File
from ..repositories.file_repository import FileRepository
from ..repositories.file_storage_repository import FileStorageRepository
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, BinaryIO
from fastapi import UploadFile
from bson import ObjectId

class FileUseCases:
    def __init__(
        self, 
        file_repository: FileRepository, 
        file_storage_repository: FileStorageRepository
    ):
        self.file_repository = file_repository
        self.file_storage_repository = file_storage_repository
    
    async def upload_file(
        self, 
        upload_file: UploadFile, 
        owner_id: str,
        parent_folder_id: Optional[str] = None
    ) -> File:
        # Generate unique filename
        unique_filename = f"{uuid.uuid4().hex}_{upload_file.filename}"
        
        # Save file to storage
        stored_filename = await self.file_storage_repository.save(upload_file, unique_filename)
        
        # Create file record in database
        file = File(
            filename=stored_filename,
            original_filename=upload_file.filename,
            content_type=upload_file.content_type,
            size=await self._get_file_size(upload_file),
            owner_id=ObjectId(owner_id),
            parent_folder_id=ObjectId(parent_folder_id) if parent_folder_id else None
        )
        
        return await self.file_repository.create(file)
    
    async def download_file(self, file_id: str, user_id: str) -> Optional[tuple[BinaryIO, str, str]]:
        # Get file from database
        file = await self.file_repository.get_by_id(file_id)
        if not file:
            return None
        
        # Check if user has access
        if (str(file.owner_id) != user_id and 
            ObjectId(user_id) not in file.shared_with and 
            not file.is_public):
            return None
        
        # Get file from storage
        file_content = await self.file_storage_repository.get(file.filename)
        if not file_content:
            return None
        
        return (file_content, file.original_filename, file.content_type)
    
    async def list_files(self, owner_id: str, folder_id: Optional[str] = None) -> List[File]:
        return await self.file_repository.list_by_owner(owner_id, folder_id)
    
    async def list_shared_files(self, user_id: str) -> List[File]:
        return await self.file_repository.list_shared_with_user(user_id)
    
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        # Get file from database
        file = await self.file_repository.get_by_id(file_id)
        if not file:
            return False
        
        # Check if user is owner
        if str(file.owner_id) != user_id:
            return False
        
        # Delete file from storage
        storage_deleted = await self.file_storage_repository.delete(file.filename)
        if not storage_deleted:
            return False
        
        # Delete file from database
        return await self.file_repository.delete(file_id)
    
    async def share_file(self, file_id: str, owner_id: str, shared_with_id: str) -> Optional[File]:
        # Get file from database
        file = await self.file_repository.get_by_id(file_id)
        if not file:
            return None
        
        # Check if user is owner
        if str(file.owner_id) != owner_id:
            return None
        
        # Add user to shared_with list if not already there
        if ObjectId(shared_with_id) not in file.shared_with:
            file.shared_with.append(ObjectId(shared_with_id))
            return await self.file_repository.update(file_id, {"shared_with": file.shared_with})
        
        return file
    
    async def create_public_link(self, file_id: str, owner_id: str, expires_in_days: Optional[int] = None) -> Optional[str]:
        # Get file from database
        file = await self.file_repository.get_by_id(file_id)
        if not file:
            return None
        
        # Check if user is owner
        if str(file.owner_id) != owner_id:
            return None
        
        # Generate public link
        public_link = f"/api/files/public/{uuid.uuid4().hex}"
        
        # Set expiry time if provided
        public_link_expiry = None
        if expires_in_days:
            public_link_expiry = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Update file
        updated_file = await self.file_repository.update(
            file_id, 
            {
                "is_public": True,
                "public_link": public_link,
                "public_link_expiry": public_link_expiry
            }
        )
        
        if not updated_file:
            return None
        
        return public_link
    
    async def get_file_by_public_link(self, public_link: str) -> Optional[File]:
        # Find all public files
        files = await self.file_repository.list_public_by_link(public_link)
        
        # Find the file with matching public link
        for file in files:
            # Check if link is expired
            if file.public_link_expiry and file.public_link_expiry < datetime.utcnow():
                continue
            
            return file
        
        return None
    
    async def _get_file_size(self, file: UploadFile) -> int:
        # Save current position
        current_position = file.file.tell()
        
        # Go to end of file to get size
        file.file.seek(0, 2)
        size = file.file.tell()
        
        # Go back to original position
        file.file.seek(current_position)
        
        return size
