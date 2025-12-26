from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from .schemas import PostCreate, PostResponse
from .database import create_db_and_tables, get_async_session, Post
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    session: AsyncSession = Depends(get_async_session)) -> Post:

    post = Post(
        caption=caption,
        url="Dummy ULR",
        file_type="photo",
        file_name="dummy name"
    )
    session.add(post)
    
    await session.commit()
    await session.refresh(post)

    return post

@app.get("/feed")
async def get_feed(session: AsyncSession = Depends(get_async_session)) -> dict[str, list]:
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "caption": post.caption,
                "url": post.url,
                "file_name": post.file_type,
                "file_type": post.file_name,
                "created_at": post.created_at.isoformat(),
            }
        )

    return {"posts": posts_data}