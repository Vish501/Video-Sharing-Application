from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from VideoSharingApp.database import get_async_session, Post, User
from VideoSharingApp.users import current_active_user

router = APIRouter(prefix="/feed", tags=["feed"])

@router.get("/")
async def get_feed(session: AsyncSession = Depends(get_async_session), user: User = Depends(current_active_user)) -> dict[str, list]:
    """
    Fetch the global feed ordered by most recent posts.
    """
    posts = (await session.execute(select(Post).order_by(Post.created_at.desc()))).scalars().all()

    users = (await session.execute(select(User))).scalars().all()
    users_map = {u.id: u.email for u in users}

    posts_data = [
        {
            "id": str(post.id),
            "user_id": str(post.user_id),
            "caption": post.caption,
            "url": post.image_url,
            "file_name": post.file_name,
            "file_type": post.file_type,
            "created_at": post.created_at.isoformat(),
            "is_owner": post.user_id == user.id,
            "email": users_map.get(post.user_id)
        }
        for post in posts
    ]

    return {"posts": posts_data}
