import shutil, os, uuid, tempfile
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from VideoSharingApp.database import get_async_session, Post, User
from VideoSharingApp.users import current_active_user
from VideoSharingApp.core.dependencies import get_imagekit
from VideoSharingApp.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/posts", tags=["posts"])

class PostRead(BaseModel):
    """
    Public-facing representation of a Post object.

    This schema is used for responses returned by FastAPI endpoints.
    It intentionally exposes only safe, read-only fields to:
    - Prevent accidental data leaks (e.g., internal IDs, foreign keys)
    - Decouple API responses from SQLAlchemy ORM models
    - Provide a stable contract for frontend consumers
    """
    id: UUID
    caption: str
    image_url: str
    file_type: str  # Expected values: "image" | "video"
    created_at: datetime

    # Enables creation of this schema directly from SQLAlchemy ORM objects
    model_config = ConfigDict(from_attributes=True)


class PostDeleteResponse(BaseModel):
    """
    Standard response schema for successful delete operations.

    While DELETE endpoints often return HTTP 204 (No Content),
    this schema can be used when an explicit success payload
    is required by the client (e.g., frontend confirmation).
    """
    success: bool


@router.post("/upload", response_model=PostRead)
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
    imagekit=Depends(get_imagekit)
):
    """
    Upload an image or video and create a post owned by the authenticated user.
    """ 
    
    temp_file_path = None
    upload_result = None
    
    try:
        suffix = os.path.splitext(file.filename)[-1]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
        
        with open(temp_file_path, "rb") as f:
            upload_result = imagekit.files.upload(
                file=f,
                file_name=file.filename,
                use_unique_file_name=True,
                tags=["backend-upload"],
            )

        post = Post(
            user_id = user.id,
            caption=caption,
            image_url=upload_result.url,
            file_type="video" if file.content_type.startswith("video/") else "image",
            file_name=upload_result.name,
        )

        session.add(post)

        await session.commit()
        await session.refresh(post)

        return post
    
    except Exception as e:
        logger.exception(f"Failed to upload post: {e}")
        raise HTTPException(status_code=500, detail="Upload failed") from e

    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        await file.close()


@router.delete("/{post_id}", response_model=PostDeleteResponse)
async def delete_post(
    post_id: str,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_active_user)
):
    """
    Delete a post owned by the authenticated user.
    """
    try:
        try:
            post_uuid = uuid.UUID(post_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid post ID")

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post = result.scalars().first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized.")

        await session.delete(post)
        await session.commit()

        return PostDeleteResponse(success=True)

    except Exception as e:
        logger.exception("Failed to delete post")
        raise HTTPException(status_code=500, detail="Internal server error") from e
    