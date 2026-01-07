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

bearer_transport_v1 = BearerTransport(
    tokenUrl=AuthPaths.token_url(APIVersion.V1) # Example: api/V1/auth/jwt/login
)

def get_jwt_strategy_v1() -> JWTStrategy:
    """
    Create and configure the JWT authentication strategy.

    This strategy is responsible for:
    - Issuing short-lived access tokens
    - Validating token integrity and expiration
    - Supporting refresh token rotation

    Security decisions:
    - Short access token lifetime (15 minutes)
    - Explicit audience claim to prevent token reuse
    - HS256 symmetric signing (sufficient for single-service auth)

    Returns:
        JWTStrategy: Configured JWT strategy instance
    """
    return JWTStrategy(
        secret=SECRET,
        lifetime_seconds=900,  # 15 minutes
        token_audience="video-sharing-app",
        algorithm="HS256",
    )
