from domain.entities import File, Folder, User
from domain.repositories import FolderRepository, FileRepository, UserRepository, FileStorageRepository
from datetime import datetime, timedelta
import uuid
from typing import Optional, List, BinaryIO
from fastapi import UploadFile
from bson import ObjectId
import jwt
import bcrypt
from jwt.exceptions import InvalidTokenError

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
        unique_filename = f"{uuid.uuid4().hex}_{upload_file.filename}"
        stored_filename = await self.file_storage_repository.save(upload_file, unique_filename)
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
        file = await self.file_repository.get_by_id(file_id)
        if not file:
            return None
        if (str(file.owner_id) != user_id and 
            ObjectId(user_id) not in file.shared_with and 
            not file.is_public):
            return None
        file_content = await self.file_storage_repository.get(file.filename)
        if not file_content:
            return None
        return (file_content, file.original_filename, file.content_type)
    
    async def list_files(self, owner_id: str, folder_id: Optional[str] = None) -> List[File]:
        return await self.file_repository.list_by_owner(owner_id, folder_id)
    
    async def list_shared_files(self, user_id: str) -> List[File]:
        return await self.file_repository.list_shared_with_user(user_id)
    
    async def delete_file(self, file_id: str, user_id: str) -> bool:
        file = await self.file_repository.get_by_id(file_id)
        if not file:
            return False
        if str(file.owner_id) != user_id:
            return False
        storage_deleted = await self.file_storage_repository.delete(file.filename)
        if not storage_deleted:
            return False
        
        return await self.file_repository.delete(file_id)
    
    async def share_file(self, file_id: str, owner_id: str, shared_with_id: str) -> Optional[File]:
        file = await self.file_repository.get_by_id(file_id)
        if not file:
            return None
        if str(file.owner_id) != owner_id:
            return None
        if ObjectId(shared_with_id) not in file.shared_with:
            file.shared_with.append(ObjectId(shared_with_id))
            return await self.file_repository.update(file_id, {"shared_with": file.shared_with})
        return file
    
    async def create_public_link(self, file_id: str, owner_id: str, expires_in_days: Optional[int] = None) -> Optional[str]:
        file = await self.file_repository.get_by_id(file_id)
        if not file:
            return None
        if str(file.owner_id) != owner_id:
            return None
        public_link = f"/api/files/public/{uuid.uuid4().hex}"
        public_link_expiry = None
        if expires_in_days:
            public_link_expiry = datetime.utcnow() + timedelta(days=expires_in_days)
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
        files = await self.file_repository.list_public_by_link(public_link)
        for file in files:
            if file.public_link_expiry and file.public_link_expiry < datetime.utcnow():
                continue
            return file
        return None
    
    async def _get_file_size(self, file: UploadFile) -> int:
        current_position = file.file.tell()
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(current_position)
        return size


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
            owner_id=owner_id,
            parent_folder_id=parent_folder_id
        )
        return await self.folder_repository.create(folder)
    
    async def list_folders(self, owner_id: str, parent_folder_id: Optional[str] = None) -> List[Folder]:
        return await self.folder_repository.list_by_owner(owner_id, parent_folder_id)
    
    async def delete_folder(self, folder_id: str, owner_id: str) -> bool:
        folder = await self.folder_repository.get_by_id(folder_id)
        if not folder:
            return False
        if str(folder.owner_id) != owner_id:
            return False
        files = await self.file_repository.list_by_owner(owner_id, folder_id)
        for file in files:
            await self.file_repository.delete(str(file.id))
        subfolders = await self.folder_repository.list_by_owner(owner_id, folder_id)
        for subfolder in subfolders:
            await self.delete_folder(str(subfolder.id), owner_id)
        return await self.folder_repository.delete(folder_id)
    
    async def share_folder(self, folder_id: str, owner_id: str, shared_with_id: str) -> Optional[Folder]:
        folder = await self.folder_repository.get_by_id(folder_id)
        if not folder:
            return None
        if str(folder.owner_id) != owner_id:
            return None
        if ObjectId(shared_with_id) not in folder.shared_with:
            folder.shared_with.append(ObjectId(shared_with_id))
            return await self.folder_repository.update(folder_id, {"shared_with": folder.shared_with})
        return folder


class UserUseCases:
    def __init__(self, user_repository: UserRepository, secret_key: str):
        self.user_repository = user_repository
        self.secret_key = secret_key
    
    async def register_user(self, username: str, email: str, password: str) -> User:
        existing_user = await self.user_repository.get_by_email(email)
        if existing_user:
            raise ValueError("User with this email already exists")
        existing_username = await self.user_repository.get_by_username(username)
        if existing_username:
            raise ValueError("Username is already taken")
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        return await self.user_repository.create(user)
    
    async def authenticate_user(self, email: str, password: str) -> Optional[str]:
        user = await self.user_repository.get_by_email(email)
        if not user:
            return None
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return None
        payload = {
            "sub": str(user.id),
            "username": user.username,
            "exp": datetime.utcnow() + timedelta(days=1)
        }
        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        return token
    
    async def get_user_from_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload.get("sub")
            if not user_id:
                return None
            return await self.user_repository.get_by_id(user_id)
        except InvalidTokenError:
            return None
