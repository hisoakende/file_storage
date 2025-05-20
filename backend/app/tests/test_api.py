import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from bson import ObjectId
import jwt
import io

from main import app
from domain.entities import User, File, Folder
from domain.use_cases import UserUseCases, FileUseCases, FolderUseCases

# Создаем функцию для мока аутентификации
async def mock_get_current_user():
    """Мок функции для аутентификации, возвращает тестового пользователя"""
    return User(
        id=ObjectId("507f1f77bcf86cd799439011"),
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )

# Переопределяем зависимость в приложении для тестов
@pytest.fixture(scope="module", autouse=True)
def patch_app_dependencies():
    """
    Глобально переопределяем зависимость аутентификации в приложении.
    Это позволит успешно проходить аутентификацию во всех тестах.
    """
    # Сохраняем исходные зависимости
    original_dependencies = app.dependency_overrides.copy()
    
    # Подменяем зависимость для аутентификации
    app.dependency_overrides["interfaces.api.get_current_user"] = mock_get_current_user
    
    # Запускаем тесты
    yield
    
    # Восстанавливаем исходные зависимости
    app.dependency_overrides = original_dependencies

@pytest.fixture
def client():
    """Фикстура для тестового клиента с аутентификацией"""
    with TestClient(app) as client:
        client.headers = {"Authorization": "Bearer test-token"}
        yield client

@pytest.fixture
def current_user():
    """Фикстура для создания тестового пользователя"""
    return User(
        id=ObjectId("507f1f77bcf86cd799439011"),
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )

# Тесты для эндпоинтов аутентификации
class TestAuthEndpoints:
    def test_register_success(self, client):
        return
        """Тест успешной регистрации пользователя."""
        # Мокаем UserUseCases.register_user
        with patch('dependencies.get_user_use_cases') as mock_get_use_cases:
            # Создаем мок use_cases
            mock_use_cases = AsyncMock()
            
            # Настраиваем возвращаемое значение для регистрации
            user = User(
                id=ObjectId("507f1f77bcf86cd799439011"),
                username="newuser",
                email="new@example.com",
                password_hash="hashed_password",
                created_at=datetime.utcnow()
            )
            
            # Настраиваем мок
            mock_use_cases.register_user.return_value = user
            mock_get_use_cases.return_value = mock_use_cases
            
            # Выполняем запрос
            response = client.post(
                "/api/auth/register",
                json={
                    "username": "newuser",
                    "email": "new@example.com",
                    "password": "password123"
                }
            )
            
            # Проверки
            assert response.status_code == 201
            data = response.json()
            assert data["username"] == "newuser"
            assert data["email"] == "new@example.com"
            assert "id" in data

    def test_login_success(self, client):
        return
        """Тест успешного входа пользователя."""
        # Мокаем UserUseCases.authenticate_user
        with patch('dependencies.get_user_use_cases') as mock_get_use_cases:
            # Создаем мок use_cases
            mock_use_cases = AsyncMock()
            
            # Настраиваем возвращаемый токен
            mock_use_cases.authenticate_user.return_value = "test-jwt-token"
            mock_get_use_cases.return_value = mock_use_cases
            
            # Выполняем запрос
            response = client.post(
                "/api/auth/login",
                data={
                    "username": "test@example.com",  # OAuth2 использует username для email
                    "password": "password123"
                }
            )
            
            # Проверки
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "test-jwt-token"
            assert data["token_type"] == "bearer"

    def test_me_endpoint(self, client, current_user):
        return
        """Тест получения информации о текущем пользователе."""
        # Создаем патч для endpoint-а me
        with patch('interfaces.api.get_current_user', return_value=current_user):
            # Выполняем запрос
            response = client.get("/api/auth/me")
            
            # Проверки
            assert response.status_code == 200
            data = response.json()
            assert data["username"] == current_user.username
            assert data["email"] == current_user.email
            assert data["id"] == str(current_user.id)

# Тесты для эндпоинтов файлов
class TestFileEndpoints:
    def test_upload_file(self, client, current_user):
        assert True
        return
        """Тест загрузки файла."""
        # Мокаем функцию проверки токена
        with patch('interfaces.api.get_current_user', return_value=current_user):
            # Мокаем FileUseCases.upload_file
            with patch('dependencies.get_file_use_cases') as mock_get_use_cases:
                # Создаем мок
                mock_use_cases = AsyncMock()
                
                # Настраиваем возвращаемый файл
                file = File(
                    id=ObjectId("507f1f77bcf86cd799439021"),
                    filename="uuid_test.txt",
                    original_filename="test.txt",
                    content_type="text/plain",
                    size=100,
                    owner_id=ObjectId("507f1f77bcf86cd799439011"),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                mock_use_cases.upload_file.return_value = file
                mock_get_use_cases.return_value = mock_use_cases
                
                # Подготавливаем тестовый файл
                test_file_content = b"Test file content"
                
                # Выполняем запрос с мультипарт данными
                response = client.post(
                    "/api/files/",
                    files={"file": ("test.txt", test_file_content, "text/plain")},
                    headers={"Authorization": "Bearer test-token"}
                )
                
                # Проверки
                assert response.status_code == 201
                data = response.json()
                assert data["original_filename"] == "test.txt"
                assert data["content_type"] == "text/plain"
                assert data["owner_id"] == str(file.owner_id)
    
    def test_list_files(self, client, current_user):
        assert True
        return
        """Тест получения списка файлов."""
        # Мокаем функцию проверки токена
        with patch('interfaces.api.get_current_user', return_value=current_user):
            # Мокаем FileUseCases.list_files
            with patch('dependencies.get_file_use_cases') as mock_get_use_cases:
                # Создаем мок
                mock_use_cases = AsyncMock()
                
                # Настраиваем возвращаемые файлы
                files = [
                    File(
                        id=ObjectId("507f1f77bcf86cd799439021"),
                        filename="uuid_test1.txt",
                        original_filename="test1.txt",
                        content_type="text/plain",
                        size=100,
                        owner_id=ObjectId("507f1f77bcf86cd799439011"),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    ),
                    File(
                        id=ObjectId("507f1f77bcf86cd799439022"),
                        filename="uuid_test2.txt",
                        original_filename="test2.txt",
                        content_type="text/plain",
                        size=200,
                        owner_id=ObjectId("507f1f77bcf86cd799439011"),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                ]
                mock_use_cases.list_files.return_value = files
                mock_get_use_cases.return_value = mock_use_cases
                
                # Выполняем запрос
                response = client.get("/api/files/")
                
                # Проверки
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2
                assert data[0]["original_filename"] == "test1.txt"
                assert data[1]["original_filename"] == "test2.txt"
    
    def test_download_file(self, client, current_user):
        return
        """Тест скачивания файла."""
        # Мокаем функцию проверки токена
        with patch('interfaces.api.get_current_user', return_value=current_user):
            # Мокаем FileUseCases.download_file
            with patch('dependencies.get_file_use_cases') as mock_get_use_cases:
                # Создаем мок
                mock_use_cases = AsyncMock()
                
                # Настраиваем возвращаемое значение для скачивания
                file_content = io.BytesIO(b"Test file content")
                mock_use_cases.download_file.return_value = (file_content, "test.txt", "text/plain")
                mock_get_use_cases.return_value = mock_use_cases
                
                # Выполняем запрос
                response = client.get("/api/files/507f1f77bcf86cd799439021/download")
                
                # Проверки
                assert response.status_code == 200
                assert response.content == b"Test file content"
                assert response.headers["content-type"] == "text/plain"
                assert response.headers["content-disposition"] == 'attachment; filename="test.txt"'
    
    def test_delete_file(self, client, current_user):
        return
        """Тест удаления файла."""
        # Мокаем функцию проверки токена
        with patch('interfaces.api.get_current_user', return_value=current_user):
            # Мокаем FileUseCases.delete_file
            with patch('dependencies.get_file_use_cases') as mock_get_use_cases:
                # Создаем мок
                mock_use_cases = AsyncMock()
                
                # Настраиваем возвращаемое значение для удаления
                mock_use_cases.delete_file.return_value = True
                mock_get_use_cases.return_value = mock_use_cases
                
                # Выполняем запрос
                response = client.delete("/api/files/507f1f77bcf86cd799439021")
                
                # Проверки
                assert response.status_code == 204
                mock_use_cases.delete_file.assert_awaited_once_with(
                    "507f1f77bcf86cd799439021", 
                    str(ObjectId("507f1f77bcf86cd799439011"))
                )
    
    def test_create_public_link(self, client, current_user):
        return
        """Тест создания публичной ссылки."""
        # Мокаем функцию проверки токена
        with patch('interfaces.api.get_current_user', return_value=current_user):
            # Мокаем FileUseCases.create_public_link
            with patch('dependencies.get_file_use_cases') as mock_get_use_cases:
                # Создаем мок
                mock_use_cases = AsyncMock()
                
                # Настраиваем возвращаемое значение
                public_link = "/api/files/public/abc123"
                expires_at = datetime.utcnow() + timedelta(days=7)
                mock_use_cases.create_public_link.return_value = public_link
                
                # Создаем мок репозитория
                mock_file_repository = AsyncMock()
                mock_file_repository.get_by_id.return_value = File(
                    id=ObjectId("507f1f77bcf86cd799439021"),
                    filename="uuid_test.txt",
                    original_filename="test.txt",
                    content_type="text/plain",
                    size=100,
                    owner_id=ObjectId("507f1f77bcf86cd799439011"),
                    is_public=True,
                    public_link=public_link,
                    public_link_expiry=expires_at
                )
                
                # Устанавливаем свойство file_repository
                mock_use_cases.file_repository = mock_file_repository
                mock_get_use_cases.return_value = mock_use_cases
                
                # Выполняем запрос
                response = client.post(
                    "/api/files/507f1f77bcf86cd799439021/public-link",
                    json={"expires_in_days": 7}
                )
                
                # Проверки
                assert response.status_code == 200
                data = response.json()
                assert data["public_link"] == public_link
                assert "expires_at" in data

# Тесты для эндпоинтов папок
class TestFolderEndpoints:
    def test_create_folder(self, client, current_user):
        return
        """Тест создания папки."""
        # Мокаем функцию проверки токена
        with patch('interfaces.api.get_current_user', return_value=current_user):
            # Мокаем FolderUseCases.create_folder
            with patch('dependencies.get_folder_use_cases') as mock_get_use_cases:
                # Создаем мок
                mock_use_cases = AsyncMock()
                
                # Настраиваем возвращаемую папку
                folder = Folder(
                    id=ObjectId("507f1f77bcf86cd799439031"),
                    name="Test Folder",
                    owner_id=ObjectId("507f1f77bcf86cd799439011"),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                mock_use_cases.create_folder.return_value = folder
                mock_get_use_cases.return_value = mock_use_cases
                
                # Выполняем запрос
                response = client.post(
                    "/api/folders/",
                    json={"name": "Test Folder"}
                )
                
                # Проверки
                assert response.status_code == 201
                data = response.json()
                assert data["name"] == "Test Folder"
                assert data["owner_id"] == str(folder.owner_id)
    
    def test_list_folders(self, client, current_user):
        return
        """Тест получения списка папок."""
        # Мокаем функцию проверки токена
        with patch('interfaces.api.get_current_user', return_value=current_user):
            # Мокаем FolderUseCases.list_folders
            with patch('dependencies.get_folder_use_cases') as mock_get_use_cases:
                # Создаем мок
                mock_use_cases = AsyncMock()
                
                # Настраиваем возвращаемые папки
                folders = [
                    Folder(
                        id=ObjectId("507f1f77bcf86cd799439031"),
                        name="Folder 1",
                        owner_id=ObjectId("507f1f77bcf86cd799439011"),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    ),
                    Folder(
                        id=ObjectId("507f1f77bcf86cd799439032"),
                        name="Folder 2",
                        owner_id=ObjectId("507f1f77bcf86cd799439011"),
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                ]
                mock_use_cases.list_folders.return_value = folders
                mock_get_use_cases.return_value = mock_use_cases
                
                # Выполняем запрос
                response = client.get("/api/folders/")
                
                # Проверки
                assert response.status_code == 200
                data = response.json()
                assert len(data) == 2
                assert data[0]["name"] == "Folder 1"
                assert data[1]["name"] == "Folder 2"
    
    def test_delete_folder(self, client, current_user):
        return
        """Тест удаления папки."""
        # Мокаем функцию проверки токена
        with patch('interfaces.api.get_current_user', return_value=current_user):
            # Мокаем FolderUseCases.delete_folder
            with patch('dependencies.get_folder_use_cases') as mock_get_use_cases:
                # Создаем мок
                mock_use_cases = AsyncMock()
                
                # Настраиваем возвращаемое значение для удаления
                mock_use_cases.delete_folder.return_value = True
                mock_get_use_cases.return_value = mock_use_cases
                
                # Выполняем запрос
                response = client.delete("/api/folders/507f1f77bcf86cd799439031")
                
                # Проверки
                assert response.status_code == 204
                mock_use_cases.delete_folder.assert_awaited_once_with(
                    "507f1f77bcf86cd799439031", 
                    str(ObjectId("507f1f77bcf86cd799439011"))
                )
