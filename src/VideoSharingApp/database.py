import uuid
from collections.abc import AsyncGenerator

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, AsyncEngine

from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends, HTTPException

from VideoSharingApp.core.dependencies import get_database_url
from VideoSharingApp.utils.logger import get_logger

logger = get_logger(__name__)

# --------------------------------------------------------------------------------------
# DECLARATIVE BASE
# --------------------------------------------------------------------------------------
class Base(DeclarativeBase):
    """
    Application-wide declarative base for all SQLAlchemy ORM models.

    This class serves as the common ancestor for every ORM model in the
    application, allowing SQLAlchemy to:
    - Collect table metadata
    - Manage model mappings
    - Create database schemas via Base.metadata

    DeclarativeBase itself is abstract; defining a concrete subclass
    establishes a single ORM registry for the application.
    """
    pass

# --------------------------------------------------------------------------------------
# ORM MODELS
# --------------------------------------------------------------------------------------
class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    Application user model.

    Inherits core authentication fields from fastapi-users and
    extends them with application-specific relationships.
    - UUID primary key
    - email, hashed_password, etc
    """
    posts = relationship(
        "Post",
        back_populates="user",
        cascade="all, delete-orphan", # Delete all orphaned posts, when a user is deleted
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
    
class Post(Base):
    """
    Image/video post uploaded by a user.
    """
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    caption = Column(Text, nullable=True)
    image_url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # image | video
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="posts")

    def __repr__(self) -> str:
        return f"<Post id={self.id} user_id={self.user_id}>"

# --------------------------------------------------------------------------------------
# ENGINE AND SESSIONS
# --------------------------------------------------------------------------------------

_engine = None
_async_session_maker = None

def get_engine() -> AsyncEngine:
    """
    Return a singleton AsyncEngine instance.

    The engine is created lazily to:
    - Avoid import-time side effects
    - Allow DATABASE_URL injection (tests)
    """
    global _engine

    if _engine is None:
        _engine = create_async_engine(
            get_database_url(),
            echo=False,     # SQL debugging to False
            future=True,    # SQLAlchemy 2.0 style
        )

    return _engine

async def close_engine() -> None:
    """
    Dispose of the AsyncEngine and release all DB connections.

    Note: MUST be called on application shutdown.
    """
    global _engine, _async_session_maker

    if _engine is not None:
        await _engine.dispose()

    _engine = None
    _async_session_maker = None

def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """
    Return a singleton async sessionmaker bound to the engine.
    """
    global _async_session_maker

    if _async_session_maker is None:
        _async_session_maker = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,  # prevents detached objects
        )

    return _async_session_maker

async def create_db_and_tables() -> None:
    """
    Create all database tables.

    Intended to be executed once during application startup.
    Failure here is considered fatal and should prevent app startup.
    """
    try:
        engine = get_engine()

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    except Exception:
        logger.exception(f"Database initialization failed.")
        raise

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a transactional AsyncSession.
    - One database session per request
    - Automatically closed after request finishes
    - Rollback on exception
    """
    session_maker = get_session_maker()

    async with session_maker() as session:
        try:
            yield session

        except HTTPException:
            await session.rollback()
            raise

        except Exception as e:
            await session.rollback()
            logger.error(f"Failed to yeild async session: {e}")
            raise

async def get_user_db(session: AsyncSession = Depends(get_async_session)) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """
    FastAPI Users database adapter.

    Bridges SQLAlchemy AsyncSession with fastapi-users user persistence.
    """
    yield SQLAlchemyUserDatabase(session, User)
