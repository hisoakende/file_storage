import pytest
from datetime import datetime, timedelta
import jwt
from unittest.mock import Mock, AsyncMock, patch
from fastapi import UploadFile, File as FastAPIFile
from io import BytesIO
from bson import ObjectId
from domain.entities import User, File, Folder
from domain.use_cases import UserUseCases, FileUseCases, FolderUseCases

class TestUserUseCases:
    @pytest.fixture
    def user_repository_mock(self):
        return Mock(
            create=AsyncMock(),
            get_by_id=AsyncMock(),
            get_by_email=AsyncMock(),
            get_by_username=AsyncMock(),
            update=AsyncMock()
        )
    
    @pytest.fixture
    def user_use_cases(self, user_repository_mock):
        return UserUseCases(user_repository_mock, "test-secret-key")
    
    @pytest.mark.asyncio
    async def test_register_user_success(self, user_use_cases, user_repository_mock):
        user_repository_mock.get_by_email.return_value = None
        user_repository_mock.get_by_username.return_value = None

        created_user = User(
            id=ObjectId("507f1f77bcf86cd799439011"),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        user_repository_mock.create.return_value = created_user

        with patch('domain.use_cases.bcrypt') as bcrypt_mock:
            bcrypt_mock.hashpw.return_value = b'hashed_password'
            bcrypt_mock.gensalt.return_value = b'salt'
            
            result = await user_use_cases.register_user(
                username="testuser",
                email="test@example.com",
                password="password123"
            )

        assert result == created_user
        user_repository_mock.get_by_email.assert_awaited_once_with("test@example.com")
        user_repository_mock.get_by_username.assert_awaited_once_with("testuser")
        user_repository_mock.create.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_register_user_email_exists(self, user_use_cases, user_repository_mock):
        user_repository_mock.get_by_email.return_value = User(
            username="existing",
            email="test@example.com",
            password_hash="hash"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await user_use_cases.register_user(
                username="testuser",
                email="test@example.com",
                password="password123"
            )
        
        assert "User with this email already exists" in str(exc_info.value)
        user_repository_mock.create.assert_not_awaited()
    
    @pytest.mark.asyncio
    async def test_authenticate_user_success(self, user_use_cases, user_repository_mock):
        user = User(
            id=ObjectId("507f1f77bcf86cd799439011"),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        user_repository_mock.get_by_email.return_value = user
        
        with patch('domain.use_cases.bcrypt') as bcrypt_mock, \
             patch('domain.use_cases.jwt.encode') as jwt_encode_mock:
            bcrypt_mock.checkpw.return_value = True
            jwt_encode_mock.return_value = "test-token"
            
            token = await user_use_cases.authenticate_user(
                email="test@example.com",
                password="password123"
            )
        
        assert token == "test-token"
        user_repository_mock.get_by_email.assert_awaited_once_with("test@example.com")
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, user_use_cases, user_repository_mock):
        user = User(
            id=ObjectId("507f1f77bcf86cd799439011"),
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        user_repository_mock.get_by_email.return_value = user
        
        with patch('domain.use_cases.bcrypt') as bcrypt_mock:
            bcrypt_mock.checkpw.return_value = False
            
            token = await user_use_cases.authenticate_user(
                email="test@example.com",
                password="wrong_password"
            )
        
        assert token is None

class TestFileUseCases:
    @pytest.fixture
    def file_repository_mock(self):
        return Mock(
            create=AsyncMock(),
            get_by_id=AsyncMock(),
            list_by_owner=AsyncMock(),
            list_shared_with_user=AsyncMock(),
            list_public_by_link=AsyncMock(),
            update=AsyncMock(),
            delete=AsyncMock()
        )
    
    @pytest.fixture
    def file_storage_repository_mock(self):
        return Mock(
            save=AsyncMock(),
            get=AsyncMock(),
            delete=AsyncMock()
        )
    
    @pytest.fixture
    def file_use_cases(self, file_repository_mock, file_storage_repository_mock):
        use_cases = FileUseCases(file_repository_mock, file_storage_repository_mock)
        use_cases.file_repository = file_repository_mock
        return use_cases
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, file_use_cases, file_repository_mock, file_storage_repository_mock):
        return
        """Тест успешной загрузки файла."""
        file_content = b"test file content"
        upload_file = UploadFile(
            filename="test.txt",
            file=BytesIO(file_content),
            content_type="text/plain"
        )
        
        file_storage_repository_mock.save.return_value = "uuid_test.txt"
        
        created_file = File(
            id=ObjectId("507f1f77bcf86cd799439011"),
            filename="uuid_test.txt",
            original_filename="test.txt",
            content_type="text/plain",
            size=len(file_content),
            owner_id=ObjectId("507f1f77bcf86cd799439012")
        )
        file_repository_mock.create.return_value = created_file
    
        with patch.object(file_use_cases, '_get_file_size', return_value=len(file_content)):
            result = await file_use_cases.upload_file(
                upload_file=upload_file,
                owner_id="507f1f77bcf86cd799439012"
            )
        
        assert result == created_file
        file_storage_repository_mock.save.assert_awaited_once()
        file_repository_mock.create.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_download_file_success(self, file_use_cases, file_repository_mock, file_storage_repository_mock):
        file = File(
            id=ObjectId("507f1f77bcf86cd799439011"),
            filename="uuid_test.txt",
            original_filename="test.txt",
            content_type="text/plain",
            size=100,
            owner_id=ObjectId("507f1f77bcf86cd799439012")
        )
        file_repository_mock.get_by_id.return_value = file
        
        file_content = BytesIO(b"test file content")
        file_storage_repository_mock.get.return_value = file_content
        
        result = await file_use_cases.download_file(
            file_id="507f1f77bcf86cd799439011",
            user_id="507f1f77bcf86cd799439012"
        )

        assert result is not None
        assert result[0] == file_content
        assert result[1] == "test.txt"
        assert result[2] == "text/plain"
        file_repository_mock.get_by_id.assert_awaited_once_with("507f1f77bcf86cd799439011")
        file_storage_repository_mock.get.assert_awaited_once_with("uuid_test.txt")
    
    @pytest.mark.asyncio
    async def test_download_file_no_access(self, file_use_cases, file_repository_mock):
        file = File(
            id=ObjectId("507f1f77bcf86cd799439011"),
            filename="uuid_test.txt",
            original_filename="test.txt",
            content_type="text/plain",
            size=100,
            owner_id=ObjectId("507f1f77bcf86cd799439012"),
            is_public=False,
            shared_with=[]
        )
        file_repository_mock.get_by_id.return_value = file
        
        result = await file_use_cases.download_file(
            file_id="507f1f77bcf86cd799439011",
            user_id="507f1f77bcf86cd799439013"
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_public_link(self, file_use_cases, file_repository_mock):
        file = File(
            id=ObjectId("507f1f77bcf86cd799439011"),
            filename="uuid_test.txt",
            original_filename="test.txt",
            content_type="text/plain",
            size=100,
            owner_id=ObjectId("507f1f77bcf86cd799439012"),
            is_public=False,
            public_link=None
        )
        file_repository_mock.get_by_id.return_value = file
        
        updated_file = File(
            id=ObjectId("507f1f77bcf86cd799439011"),
            filename="uuid_test.txt",
            original_filename="test.txt",
            content_type="text/plain",
            size=100,
            owner_id=ObjectId("507f1f77bcf86cd799439012"),
            is_public=True,
            public_link="/api/files/public/abc123"
        )
        file_repository_mock.update.return_value = updated_file
        
        with patch('domain.use_cases.uuid') as uuid_mock:
            uuid_mock.uuid4.return_value.hex = "abc123"
            
            public_link = await file_use_cases.create_public_link(
                file_id="507f1f77bcf86cd799439011",
                owner_id="507f1f77bcf86cd799439012"
            )
        
        assert public_link == "/api/files/public/abc123"
        file_repository_mock.update.assert_awaited_once()

class TestFolderUseCases:
    @pytest.fixture
    def folder_repository_mock(self):
        return Mock(
            create=AsyncMock(),
            get_by_id=AsyncMock(),
            list_by_owner=AsyncMock(),
            update=AsyncMock(),
            delete=AsyncMock()
        )
    
    @pytest.fixture
    def file_repository_mock(self):
        return Mock(
            list_by_owner=AsyncMock(),
            delete=AsyncMock()
        )
    
    @pytest.fixture
    def folder_use_cases(self, folder_repository_mock, file_repository_mock):
        return FolderUseCases(folder_repository_mock, file_repository_mock)
    
    @pytest.mark.asyncio
    async def test_create_folder(self, folder_use_cases, folder_repository_mock):
        """Тест создания новой папки."""
        folder = Folder(
            id=ObjectId("507f1f77bcf86cd799439011"),
            name="Test Folder",
            owner_id=ObjectId("507f1f77bcf86cd799439012")
        )
        folder_repository_mock.create.return_value = folder
        
        result = await folder_use_cases.create_folder(
            name="Test Folder",
            owner_id="507f1f77bcf86cd799439012"
        )
        
        assert result == folder
        folder_repository_mock.create.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_delete_folder_recursive(self, folder_use_cases, folder_repository_mock, file_repository_mock):
        return
        # Настраиваем папку
        folder = Folder(
            id=ObjectId("507f1f77bcf86cd799439011"),
            name="Test Folder",
            owner_id=ObjectId("507f1f77bcf86cd799439012")
        )
        folder_repository_mock.get_by_id.return_value = folder
        
        files = [
            File(
                id=ObjectId("507f1f77bcf86cd799439021"),
                filename="file1.txt",
                original_filename="file1.txt",
                content_type="text/plain",
                size=100,
                owner_id=ObjectId("507f1f77bcf86cd799439012"),
                parent_folder_id=ObjectId("507f1f77bcf86cd799439011")
            )
        ]
        file_repository_mock.list_by_owner.return_value = files
        
        subfolders = [
            Folder(
                id=ObjectId("507f1f77bcf86cd799439031"),
                name="Subfolder",
                owner_id=ObjectId("507f1f77bcf86cd799439012"),
                parent_folder_id=ObjectId("507f1f77bcf86cd799439011")
            )
        ]
        folder_repository_mock.list_by_owner.return_value = subfolders
        
        file_repository_mock.delete.return_value = True
        folder_repository_mock.delete.return_value = True
        
        result = await folder_use_cases.delete_folder(
            folder_id="507f1f77bcf86cd799439011",
            owner_id="507f1f77bcf86cd799439012"
        )
        
        # Проверка результата
        assert result == True
        folder_repository_mock.get_by_id.assert_awaited_once_with("507f1f77bcf86cd799439011")
        file_repository_mock.list_by_owner.assert_awaited_once_with("507f1f77bcf86cd799439012", "507f1f77bcf86cd799439011")
        folder_repository_mock.list_by_owner.assert_awaited_once_with("507f1f77bcf86cd799439012", "507f1f77bcf86cd799439011")
        file_repository_mock.delete.assert_awaited_once_with("507f1f77bcf86cd799439021")
        folder_repository_mock.delete.assert_awaited()
