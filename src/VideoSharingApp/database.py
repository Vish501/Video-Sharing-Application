import uuid
from collections.abc import AsyncGenerator

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID
from fastapi import Depends

from src.VideoSharingApp.core.dependencies import get_database_url
from src.VideoSharingApp.utils.logger import get_logger

logger = get_logger(__name__)

DATABASE_URL = get_database_url()

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

engine = create_async_engine(
    DATABASE_URL,
    echo=False,     # set True for SQL debugging
    future=True,    # SQLAlchemy 2.0 style
)

async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,  # prevents detached objects
)

async def create_db_and_tables() -> None:
    """
    Create all database tables.

    Intended to be executed once during application startup.
    Failure here is considered fatal and should prevent app startup.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        logger.exception(f"Database initialization failed: {e}")
        raise

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a transactional AsyncSession.
    - One database session per request
    - Automatically closed after request finishes
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Failed to yeild async session.")
            raise
        finally:
            # session must always close no matter what
            await session.close()


async def get_user_db(session: AsyncSession = Depends(get_async_session)) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """
    FastAPI Users database adapter.

    Bridges SQLAlchemy AsyncSession with fastapi-users user persistence.
    """
    yield SQLAlchemyUserDatabase(session, User)
