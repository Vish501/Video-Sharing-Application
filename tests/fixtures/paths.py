"""
users_path_v1, feed_path_v1, posts_path_v1
"""
import os
import pytest
import uuid

from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport, Response
from typing import AsyncGenerator, Callable, Awaitable

from VideoSharingApp.app import app
from VideoSharingApp.core.dependencies import get_imagekit
from VideoSharingApp.constants.auth import AuthPaths, APIVersion

pytestmark = pytest.mark.asyncio

# ---------------------------------------------------------------------
# API PATH FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture
def users_path_v1() -> str:
    """
    Path to the authenticated user endpoint.
    """
    return f"{AuthPaths.user_prefix(APIVersion.V1)}/me"


@pytest.fixture
def feed_path_v1() -> str:
    """
    Path to the global feed endpoint.
    """
    return f"{AuthPaths.base_prefix(APIVersion.V1)}/feed/"


@pytest.fixture
def posts_path_v1() -> str:
    """
    Base path for post-related endpoints.
    """
    return f"{AuthPaths.base_prefix(APIVersion.V1)}/posts"