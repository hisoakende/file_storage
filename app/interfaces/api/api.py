from fastapi import APIRouter
from .auth_router import router as auth_router
from .file_router import router as file_router
from .folder_router import router as folder_router

router = APIRouter(prefix="/api")
router.include_router(auth_router)
router.include_router(file_router)
router.include_router(folder_router)
