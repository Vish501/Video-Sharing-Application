import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from fastapi_users.db import SQLAlchemyUserDatabase, SQLAlchemyBaseUserTableUUID

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
