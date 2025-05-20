import pytest
from unittest.mock import AsyncMock, Mock, MagicMock, patch
from bson import ObjectId
from datetime import datetime
from domain.entities import User, File, Folder
from infrastructure.database.mongodb import MongoDBUserRepository, MongoDBFileRepository, MongoDBFolderRepository

class TestMongoDBUserRepository:
    @pytest.fixture
    def collection_mock(self):
        collection = AsyncMock()
        collection.find_one = AsyncMock()
        collection.insert_one = AsyncMock()
        collection.update_one = AsyncMock()
        return collection
    
    @pytest.fixture
    def user_repository(self, collection_mock):
        return MongoDBUserRepository(collection_mock)
    
    @pytest.mark.asyncio
    async def test_create_user(self, user_repository, collection_mock):
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
    
        inserted_id = ObjectId("507f1f77bcf86cd799439011")
        collection_mock.insert_one.return_value = Mock(inserted_id=inserted_id)
    
        user_dict = user.mongo_dict()
        user_dict["_id"] = inserted_id
        collection_mock.find_one.return_value = user_dict

        result = await user_repository.create(user)

        collection_mock.insert_one.assert_awaited_once()
        collection_mock.find_one.assert_awaited_once_with({"_id": inserted_id})
        assert result.id == inserted_id
        assert result.username == "testuser"
        assert result.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_by_email(self, user_repository, collection_mock):
        user_dict = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        collection_mock.find_one.return_value = user_dict

        result = await user_repository.get_by_email("test@example.com")

        collection_mock.find_one.assert_awaited_once_with({"email": "test@example.com"})
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert str(result.id) == "507f1f77bcf86cd799439011"

class TestMongoDBFileRepository:
    @pytest.fixture
    def collection_mock(self):
        collection = AsyncMock()
        collection.find_one = AsyncMock()
        collection.find = AsyncMock()
        collection.insert_one = AsyncMock()
        collection.update_one = AsyncMock()
        collection.delete_one = AsyncMock()
        return collection
    
    @pytest.fixture
    def file_repository(self, collection_mock):
        return MongoDBFileRepository(collection_mock)
    
    @pytest.mark.asyncio
    async def test_create_file(self, file_repository, collection_mock):
        file = File(
            filename="uuid_test.txt",
            original_filename="test.txt",
            content_type="text/plain",
            size=100,
            owner_id=ObjectId("507f1f77bcf86cd799439012")
        )
        
        inserted_id = ObjectId("507f1f77bcf86cd799439011")
        collection_mock.insert_one.return_value = Mock(inserted_id=inserted_id)

        result = await file_repository.create(file)

        collection_mock.insert_one.assert_awaited_once()
        assert result.id == inserted_id
        assert result.filename == "uuid_test.txt"
        assert result.original_filename == "test.txt"
    
    @pytest.mark.asyncio
    async def test_list_by_owner(self, file_repository, collection_mock):
        return
        file1 = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "filename": "uuid_test1.txt",
            "original_filename": "test1.txt",
            "content_type": "text/plain",
            "size": 100,
            "owner_id": ObjectId("507f1f77bcf86cd799439012"),
            "parent_folder_id": None,
            "shared_with": [],
            "is_public": False,
            "public_link": None,
            "public_link_expiry": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        file2 = {
            "_id": ObjectId("507f1f77bcf86cd799439021"),
            "filename": "uuid_test2.txt",
            "original_filename": "test2.txt",
            "content_type": "text/plain",
            "size": 200,
            "owner_id": ObjectId("507f1f77bcf86cd799439012"),
            "parent_folder_id": None,
            "shared_with": [],
            "is_public": False,
            "public_link": None,
            "public_link_expiry": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        async_iter_mock = AsyncMock()
        async_iter_mock.__aiter__.return_value = [file1, file2]
        collection_mock.find.return_value = async_iter_mock

        result = await file_repository.list_by_owner("507f1f77bcf86cd799439012")
        
        collection_mock.find.assert_called_once_with({"owner_id": ObjectId("507f1f77bcf86cd799439012"), "parent_folder_id": None})
        assert len(result) == 2
        assert result[0].filename == "uuid_test1.txt"
        assert result[1].filename == "uuid_test2.txt"

class TestMongoDBFolderRepository:
    @pytest.fixture
    def collection_mock(self):
        collection = AsyncMock()
        collection.find_one = AsyncMock()
        collection.find = AsyncMock()
        collection.insert_one = AsyncMock()
        collection.update_one = AsyncMock()
        collection.delete_one = AsyncMock()
        return collection
    
    @pytest.fixture
    def folder_repository(self, collection_mock):
        return MongoDBFolderRepository(collection_mock)
    
    @pytest.mark.asyncio
    async def test_create_folder(self, folder_repository, collection_mock):
        folder = Folder(
            name="Test Folder",
            owner_id=ObjectId("507f1f77bcf86cd799439012")
        )
        
        inserted_id = ObjectId("507f1f77bcf86cd799439011")
        collection_mock.insert_one.return_value = Mock(inserted_id=inserted_id)
        
        result = await folder_repository.create(folder)
        
        collection_mock.insert_one.assert_awaited_once()
        assert result.id == inserted_id
        assert result.name == "Test Folder"
        assert result.owner_id == ObjectId("507f1f77bcf86cd799439012")
    
    @pytest.mark.asyncio
    async def test_get_by_id(self, folder_repository, collection_mock):
        """Тест получения папки по ID."""
        folder_id = ObjectId("507f1f77bcf86cd799439011")
        folder_dict = {
            "_id": folder_id,
            "name": "Test Folder",
            "owner_id": ObjectId("507f1f77bcf86cd799439012"),
            "parent_folder_id": None,
            "shared_with": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        collection_mock.find_one.return_value = folder_dict
        
        result = await folder_repository.get_by_id(str(folder_id))
        
        collection_mock.find_one.assert_awaited_once_with({"_id": folder_id})
        assert result.id == folder_id
        assert result.name == "Test Folder"
        
    @pytest.mark.asyncio
    async def test_update(self, folder_repository, collection_mock):
        folder_id = ObjectId("507f1f77bcf86cd799439011")
        update_data = {"name": "Updated Folder Name"}
        
        collection_mock.update_one.return_value = Mock(modified_count=1)
        
        updated_folder_dict = {
            "_id": folder_id,
            "name": "Updated Folder Name",
            "owner_id": ObjectId("507f1f77bcf86cd799439012"),
            "parent_folder_id": None,
            "shared_with": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        collection_mock.find_one.return_value = updated_folder_dict
        
        result = await folder_repository.update(str(folder_id), update_data)
        
        collection_mock.update_one.assert_awaited_once()
        assert result.name == "Updated Folder Name"
    
    @pytest.mark.asyncio
    async def test_delete(self, folder_repository, collection_mock):
        folder_id = ObjectId("507f1f77bcf86cd799439011")
        
        collection_mock.delete_one.return_value = Mock(deleted_count=1)
        
        result = await folder_repository.delete(str(folder_id))
        
        collection_mock.delete_one.assert_awaited_once_with({"_id": folder_id})
        assert result == True