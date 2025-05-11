from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from ...domain.use_cases.folder_use_cases import FolderUseCases
from ...domain.entities.user import User
from ..serializers.folder_serializers import FolderRequest, FolderResponse
from .auth_router import get_current_user

router = APIRouter(prefix="/folders", tags=["folders"])

@router.post("/", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    folder_data: FolderRequest,
    current_user: User = Depends(get_current_user),
    folder_use_cases: FolderUseCases = Depends()
):
    folder = await folder_use_cases.create_folder(
        name=folder_data.name,
        owner_id=str(current_user.id),
        parent_folder_id=folder_data.parent_folder_id
    )
    
    return {
        "id": str(folder.id),
        "name": folder.name,
        "owner_id": str(folder.owner_id),
        "parent_folder_id": str(folder.parent_folder_id) if folder.parent_folder_id else None,
        "shared_with": [str(user_id) for user_id in folder.shared_with],
        "created_at": folder.created_at,
        "updated_at": folder.updated_at
    }

@router.get("/", response_model=List[FolderResponse])
async def list_folders(
    parent_folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    folder_use_cases: FolderUseCases = Depends()
):
    folders = await folder_use_cases.list_folders(
        owner_id=str(current_user.id),
        parent_folder_id=parent_folder_id
    )
    
    return [
        {
            "id": str(folder.id),
            "name": folder.name,
            "owner_id": str(folder.owner_id),
            "parent_folder_id": str(folder.parent_folder_id) if folder.parent_folder_id else None,
            "shared_with": [str(user_id) for user_id in folder.shared_with],
            "created_at": folder.created_at,
            "updated_at": folder.updated_at
        }
        for folder in folders
    ]

@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: str,
    current_user: User = Depends(get_current_user),
    folder_use_cases: FolderUseCases = Depends()
):
    deleted = await folder_use_cases.delete_folder(folder_id, str(current_user.id))
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found or you don't have access to delete it"
        )

@router.post("/{folder_id}/share", response_model=FolderResponse)
async def share_folder(
    folder_id: str,
    share_data: ShareFileRequest,  # Reusing the same schema
    current_user: User = Depends(get_current_user),
    folder_use_cases: FolderUseCases = Depends()
):
    shared_folder = await folder_use_cases.share_folder(
        folder_id=folder_id,
        owner_id=str(current_user.id),
        shared_with_id=share_data.user_id
    )
    
    if not shared_folder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Folder not found or you don't have access to share it"
        )
    
    return {
        "id": str(shared_folder.id),
        "name": shared_folder.name,
        "owner_id": str(shared_folder.owner_id),
        "parent_folder_id": str(shared_folder.parent_folder_id) if shared_folder.parent_folder_id else None,
        "shared_with": [str(user_id) for user_id in shared_folder.shared_with],
        "created_at": shared_folder.created_at,
        "updated_at": shared_folder.updated_at
    }
