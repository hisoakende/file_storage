from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
from functools import lru_cache
from domain.use_cases import UserUseCases, FileUseCases, FolderUseCases
from infrastructure.database.mongodb import MongoDBUserRepository, MongoDBFileRepository, MongoDBFolderRepository
from infrastructure.database.local_file_storage_repository import LocalFileStorageRepository

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "file_storage")
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

os.makedirs(STORAGE_PATH, exist_ok=True)

@lru_cache
def get_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    return client[MONGODB_DB_NAME]

def get_user_repository():
    db = get_database()
    return MongoDBUserRepository(db["users"])

def get_file_repository():
    db = get_database()
    return MongoDBFileRepository(db["files"])

def get_folder_repository():
    db = get_database()
    return MongoDBFolderRepository(db["folders"])

def get_file_storage_repository():
    return LocalFileStorageRepository(STORAGE_PATH)

def get_user_use_cases(user_repository=Depends(get_user_repository)):
    return UserUseCases(user_repository, SECRET_KEY)

def get_file_use_cases(
    file_repository=Depends(get_file_repository),
    file_storage_repository=Depends(get_file_storage_repository)
):
    return FileUseCases(file_repository, file_storage_repository)

def get_folder_use_cases(
    folder_repository=Depends(get_folder_repository),
    file_repository=Depends(get_file_repository)
):
    return FolderUseCases(folder_repository, file_repository)
