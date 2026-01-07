import uuid
import os
from typing import Optional
from dotenv import load_dotenv

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase

from src.VideoSharingApp.database import User, get_user_db
from src.VideoSharingApp.utils.logger import get_logger
from src.VideoSharingApp.constants.auth import AuthPaths, APIVersion

load_dotenv()

logger = get_logger(__name__)

SECRET = os.environ.get("JWT_SECRET_TOKEN")
if not SECRET or not SECRET.strip():
    raise RuntimeError("JWT_SECRET_TOKEN environment variable cannot be empty.")

class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """
    Handles user-related business logic and lifecycle events.

    This class is intentionally thin at first, but serves as the
    extension point for:
    - Custom validation
    - Email workflows
    - Auditing / analytics hooks
    """
    
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request]=None):
        logger.info("User registered",
                    extra={"user_id": str(user.id)}
        )

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request]=None):
        logger.info("Password reset requested",
            extra={"user_id": str(user.id)},
        )

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        logger.info(
            "Email verification requested",
            extra={"user_id": str(user.id)},
        )
    
async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """
    Provides a UserManager instance per request.
    """
    yield UserManager(user_db)
