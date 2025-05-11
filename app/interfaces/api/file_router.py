from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File as FastAPIFile
from fastapi.responses import StreamingResponse
from typing import List, Optional
from ...domain.use_cases.file_use_cases import FileUseCases
from ...domain.entities.user import User
from ..serializers.file_serializers import FileResponse, ShareFileRequest, CreatePublicLinkRequest, PublicLinkResponse
from .auth_router import get_current_user

router = APIRouter(prefix="/files", tags=["files"])

@router.post("/", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends()
):
    uploaded_file = await file_use_cases.upload_file(
        upload_file=file,
        owner_id=str(current_user.id),
        parent_folder_id=folder_id
    )
    
    return {
        "id": str(uploaded_file.id),
        "filename": uploaded_file.filename,
        "original_filename": uploaded_file.original_filename,
        "content_type": uploaded_file.content_type,
        "size": uploaded_file.size,
        "owner_id": str(uploaded_file.owner_id),
        "parent_folder_id": str(uploaded_file.parent_folder_id) if uploaded_file.parent_folder_id else None,
        "shared_with": [str(user_id) for user_id in uploaded_file.shared_with],
        "is_public": uploaded_file.is_public,
        "public_link": uploaded_file.public_link,
        "public_link_expiry": uploaded_file.public_link_expiry,
        "created_at": uploaded_file.created_at,
        "updated_at": uploaded_file.updated_at
    }

@router.get("/", response_model=List[FileResponse])
async def list_files(
    folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends()
):
    files = await file_use_cases.list_files(
        owner_id=str(current_user.id),
        folder_id=folder_id
    )
    
    return [
        {
            "id": str(file.id),
            "filename": file.filename,
            "original_filename": file.original_filename,
            "content_type": file.content_type,
            "size": file.size,
            "owner_id": str(file.owner_id),
            "parent_folder_id": str(file.parent_folder_id) if file.parent_folder_id else None,
            "shared_with": [str(user_id) for user_id in file.shared_with],
            "is_public": file.is_public,
            "public_link": file.public_link,
            "public_link_expiry": file.public_link_expiry,
            "created_at": file.created_at,
            "updated_at": file.updated_at
        }
        for file in files
    ]

@router.get("/shared", response_model=List[FileResponse])
async def list_shared_files(
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends()
):
    files = await file_use_cases.list_shared_files(user_id=str(current_user.id))
    
    return [
        {
            "id": str(file.id),
            "filename": file.filename,
            "original_filename": file.original_filename,
            "content_type": file.content_type,
            "size": file.size,
            "owner_id": str(file.owner_id),
            "parent_folder_id": str(file.parent_folder_id) if file.parent_folder_id else None,
            "shared_with": [str(user_id) for user_id in file.shared_with],
            "is_public": file.is_public,
            "public_link": file.public_link,
            "public_link_expiry": file.public_link_expiry,
            "created_at": file.created_at,
            "updated_at": file.updated_at
        }
        for file in files
    ]

@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends()
):
    file_tuple = await file_use_cases.download_file(file_id, str(current_user.id))
    if not file_tuple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to it"
        )
    
    file, _, _ = file_tuple
    
    # Get file details
    file_details = await file_use_cases.file_repository.get_by_id(file_id)
    
    return {
        "id": str(file_details.id),
        "filename": file_details.filename,
        "original_filename": file_details.original_filename,
        "content_type": file_details.content_type,
        "size": file_details.size,
        "owner_id": str(file_details.owner_id),
        "parent_folder_id": str(file_details.parent_folder_id) if file_details.parent_folder_id else None,
        "shared_with": [str(user_id) for user_id in file_details.shared_with],
        "is_public": file_details.is_public,
        "public_link": file_details.public_link,
        "public_link_expiry": file_details.public_link_expiry,
        "created_at": file_details.created_at,
        "updated_at": file_details.updated_at
    }

@router.get("/{file_id}/download")
async def download_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends()
):
    file_tuple = await file_use_cases.download_file(file_id, str(current_user.id))
    if not file_tuple:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to it"
        )
    
    file_content, original_filename, content_type = file_tuple
    
    return StreamingResponse(
        content=file_content,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename=\"{original_filename}\""}
    )

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends()
):
    deleted = await file_use_cases.delete_file(file_id, str(current_user.id))
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to delete it"
        )

@router.post("/{file_id}/share", response_model=FileResponse)
async def share_file(
    file_id: str,
    share_data: ShareFileRequest,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends()
):
    shared_file = await file_use_cases.share_file(
        file_id=file_id,
        owner_id=str(current_user.id),
        shared_with_id=share_data.user_id
    )
    
    if not shared_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to share it"
        )
    
    return {
        "id": str(shared_file.id),
        "filename": shared_file.filename,
        "original_filename": shared_file.original_filename,
        "content_type": shared_file.content_type,
        "size": shared_file.size,
        "owner_id": str(shared_file.owner_id),
        "parent_folder_id": str(shared_file.parent_folder_id) if shared_file.parent_folder_id else None,
        "shared_with": [str(user_id) for user_id in shared_file.shared_with],
        "is_public": shared_file.is_public,
        "public_link": shared_file.public_link,
        "public_link_expiry": shared_file.public_link_expiry,
        "created_at": shared_file.created_at,
        "updated_at": shared_file.updated_at
    }

@router.post("/{file_id}/public-link", response_model=PublicLinkResponse)
async def create_public_link(
    file_id: str,
    link_data: CreatePublicLinkRequest,
    current_user: User = Depends(get_current_user),
    file_use_cases: FileUseCases = Depends()
):
    public_link = await file_use_cases.create_public_link(
        file_id=file_id,
        owner_id=str(current_user.id),
        expires_in_days=link_data.expires_in_days
    )
    
    if not public_link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have access to create a public link"
        )
    
    # Get file to get expiry time
    file = await file_use_cases.file_repository.get_by_id(file_id)
    
    return {
        "public_link": public_link,
        "expires_at": file.public_link_expiry
    }

@router.get("/public/{public_key}")
async def access_public_file(
    public_key: str,
    file_use_cases: FileUseCases = Depends()
):
    public_link = f"/api/files/public/{public_key}"
    file = await file_use_cases.get_file_by_public_link(public_link)
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Public file not found or link has expired"
        )
    
    file_content = await file_use_cases.file_storage_repository.get(file.filename)
    
    if not file_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File content not found"
        )
    
    return StreamingResponse(
        content=file_content,
        media_type=file.content_type,
        headers={"Content-Disposition": f"attachment; filename=\"{file.original_filename}\""}
    )
