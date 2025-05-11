from fastapi import FastAPI, Depends
from motor.motor_asyncio import AsyncIOMotorClient
import os
from .interfaces.api.api import router as api_router
from .domain.use_cases.user_use_cases import UserUseCases
from .domain.use_cases.file_use_cases import FileUseCases
from .domain.use_cases.folder_use_cases import FolderUseCases
from .infrastructure.database.mongodb_user_repository import MongoDBUserRepository
from .infrastructure.database.mongodb_file_repository import MongoDBFileRepository
from .infrastructure.database.mongodb_folder_repository import MongoDBFolderRepository
from .infrastructure.storage.local_file_storage_repository import LocalFileStorageRepository
from functools import lru_cache

app = FastAPI(title="File Storage API")

# Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "file_storage")
STORAGE_PATH = os.getenv("STORAGE_PATH", "./storage")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")

# Database connection
@lru_cache
def get_database():
    client = AsyncIOMotorClient(MONGODB_URL)
    return client[MONGODB_DB_NAME]

# Repositories
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

# Use cases
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

# Register dependencies
app.dependency_overrides[UserUseCases] = get_user_use_cases
app.dependency_overrides[FileUseCases] = get_file_use_cases
app.dependency_overrides[FolderUseCases] = get_folder_use_cases

# Include API routes
app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to File Storage API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
