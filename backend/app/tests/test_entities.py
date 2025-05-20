import pytest
from datetime import datetime
from bson import ObjectId
from domain.entities import User, File, Folder

class TestUser:
    def test_user_creation(self):
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)

    def test_user_mongo_dict(self):
        user = User(
            id=ObjectId("507f1f77bcf86cd799439011"),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        mongo_dict = user.mongo_dict()
        assert "_id" in mongo_dict
        # Проверяем либо строки, либо преобразуем обратно в ObjectId
        if isinstance(mongo_dict["_id"], str):
            assert mongo_dict["_id"] == str(ObjectId("507f1f77bcf86cd799439011"))
        else:
            assert mongo_dict["_id"] == ObjectId("507f1f77bcf86cd799439011")

    def test_user_from_mongo(self):
        mongo_data = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "username": "testuser",
            "email": "test@example.com",
            "password_hash": "hashed_password",
            "created_at": datetime(2023, 1, 1, 12, 0, 0),
            "updated_at": datetime(2023, 1, 1, 12, 0, 0)
        }
        user = User.from_mongo(mongo_data)
        assert str(user.id) == "507f1f77bcf86cd799439011"
        assert user.username == "testuser"
        assert user.email == "test@example.com"

class TestFile:
    def test_file_creation(self):
        file = File(
            filename="uuid_filename.txt",
            original_filename="test.txt",
            content_type="text/plain",
            size=1024,
            owner_id=ObjectId("507f1f77bcf86cd799439011")
        )
        assert file.filename == "uuid_filename.txt"
        assert file.original_filename == "test.txt"
        assert file.content_type == "text/plain"
        assert file.size == 1024
        assert file.owner_id == ObjectId("507f1f77bcf86cd799439011")
        assert file.is_public == False
        assert file.shared_with == []

    def test_file_public_link(self):
        file = File(
            filename="uuid_filename.txt",
            original_filename="test.txt",
            content_type="text/plain",
            size=1024,
            owner_id=ObjectId("507f1f77bcf86cd799439011"),
            is_public=True,
            public_link="/api/files/public/abc123",
            public_link_expiry=datetime(2023, 12, 31, 23, 59, 59)
        )
        assert file.is_public == True
        assert file.public_link == "/api/files/public/abc123"
        assert file.public_link_expiry == datetime(2023, 12, 31, 23, 59, 59)

class TestFolder:
    def test_folder_creation(self):
        folder = Folder(
            name="Test Folder",
            owner_id=ObjectId("507f1f77bcf86cd799439011")
        )
        assert folder.name == "Test Folder"
        assert folder.owner_id == ObjectId("507f1f77bcf86cd799439011")
        assert folder.parent_folder_id is None
        assert folder.shared_with == []

    def test_folder_with_parent(self):
        folder = Folder(
            name="Subfolder",
            owner_id=ObjectId("507f1f77bcf86cd799439011"),
            parent_folder_id=ObjectId("507f1f77bcf86cd799439012")
        )
        assert folder.name == "Subfolder"
        assert folder.parent_folder_id == ObjectId("507f1f77bcf86cd799439012")

    def test_folder_with_shared_access(self):
        folder = Folder(
            name="Shared Folder",
            owner_id=ObjectId("507f1f77bcf86cd799439011"),
            shared_with=[ObjectId("507f1f77bcf86cd799439013"), ObjectId("507f1f77bcf86cd799439014")]
        )
        assert len(folder.shared_with) == 2
        assert ObjectId("507f1f77bcf86cd799439013") in folder.shared_with
        assert ObjectId("507f1f77bcf86cd799439014") in folder.shared_with
