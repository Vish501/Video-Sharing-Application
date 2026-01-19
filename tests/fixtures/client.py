"""
async_client, anyio_backend
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
# PYTEST / ASYNCIO CONFIGURATION
# ---------------------------------------------------------------------

@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Force pytest-anyio to use asyncio instead of trio.

    Required for compatibility with FastAPI + AsyncClient.
    """
    return "asyncio"

# ---------------------------------------------------------------------
# HTTP CLIENT & APPLICATION LIFESPAN
# ---------------------------------------------------------------------

@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an isolated AsyncClient bound directly to the FastAPI app.

    Scoped as a fixuture:
    - Manages application startup/shutdown via LifespanManager
    - Avoids running a live server
    - Prevents cross-test state leakage, even when tests are run in parallel,
    thereby ensuring test isolation

    Scope:
    - Function-scoped to ensure clean state per test
    """
    async with LifespanManager(app):
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
