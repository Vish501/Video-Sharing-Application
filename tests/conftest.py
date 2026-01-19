"""
Global pytest fixtures for API tests.

This file defines:
- Application lifecycle management (FastAPI lifespan)
- HTTP client setup
- Authentication helpers
- Common API paths
- External service mocking (ImageKit)

These fixtures are shared across all test modules.
"""

import os
import pytest

# =============================================================================
# ENVIRONMENT BOOTSTRAP (must run before app import)
# =============================================================================

@pytest.fixture(autouse=True)
def inject_test_database_url(tmp_path_factory) -> None:
    """
    Inject a temporary SQLite DATABASE_URL for the entire test session.

    This runs BEFORE the FastAPI app is imported, ensuring that:
    - database.py reads the test URL
    - engine is created correctly
    - lifespan creates tables in the temp DB
    """
    db_dir = tmp_path_factory.mktemp("db")
    db_path = db_dir / "test.db"
    test_db_url = f"sqlite+aiosqlite:///{db_path}"

    os.environ["DATABASE_URL"] = test_db_url

# =============================================================================
# APPLICATION FIXTURES (must be run after ENVIRONMENT BOOTSTRAP)
# =============================================================================
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

# ---------------------------------------------------------------------
# AUTHENTICATION & USER FIXTURES
# ---------------------------------------------------------------------

@pytest.fixture
def test_user() -> dict[str, str]:
    """
    Canonical test user payload.

    Used when a deterministic, reusable user is required.
    """
    return {
        "email": "testuser@example.com",
        "password": "password123@",
    }


@pytest.fixture
def register_user_v1(async_client) -> Callable[[dict[str, str]], Awaitable[Response]]:
    """
    Factory fixture that returns a callable for user registration (v1).

    Usage:
    - response = await register_user_v1({
            "email": "x@example.com",
            "password": "secret"
        })
    """
    async def _register(user: dict):
        auth_prefix = AuthPaths.router_prefix(APIVersion.V1)

        return await async_client.post(
            f"{auth_prefix}/register",
            json=user
        )

    return _register


@pytest.fixture
async def login_user_v1(async_client) -> Callable[[dict], Awaitable[Response]]:
    """
    Factory fixture that returns a callable for user login (v1).

    Usage:
    - response = await login_user_v1(email, password)
    """
    async def _login(email: str, password: str):
        auth_prefix = AuthPaths.router_prefix(APIVersion.V1)

        return await async_client.post(
            f"{auth_prefix}/login",
            data = {
                "username": email,
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    
    return _login


@pytest.fixture
async def auth_user(register_user_v1, login_user_v1):
    """
    Factory fixture that:
    - Registers a user
    - Logs them in
    - Returns Authorization headers

    Supports:
    - Multiple users per test
    - Automatic unique email generation
    """
    async def _create_user(email: str | None = None, password: str = "password123@") -> dict[str, str]:
        if email is None:
            email = f"user_{uuid.uuid4()}@example.com"

        register_response = await register_user_v1({
            "email": email,
            "password": password,
        })
        assert register_response.status_code in (200, 201)
        
        login_response = await login_user_v1(email, password)
        assert login_response.status_code in (200, 201)

        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    return _create_user


@pytest.fixture
async def auth_headers(auth_user, test_user):
    """
    Convenience fixture to login and register a pre-configured 
    user from the `test_user` fixture.

    Intended for:
    - Simple tests
    - Single-user scenarios
    """
    user_header = await auth_user(
        email = test_user["email"],
        password = test_user["password"]
    )

    return user_header


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


# ---------------------------------------------------------------------
# IMAGEKIT MOCKING
# ---------------------------------------------------------------------

class FakeImageKit:
    """
    Lightweight mock replacement for the ImageKit client.

    This mock mimics only the subset of ImageKit behavior that
    the /posts/upload endpoint relies on:
    - imagekit.files.upload(...)
    - calling upload result for `.url` and `.name` attributes
    """
    class FakeUploadResult:
        """
        Mimics successful upload ImageKit response object.
        """
        def __init__(self) -> None:
            self.url = "https://example.com/fake.jpg"
            self.name = "fake.jpg"

    class files:
        """
        Mimics the `imagekit.files` namespace.
        """
        @staticmethod
        def upload(*args, **kwargs):
            """
            Fake upload method.

            Ignores input arguments and always returns
            a successful upload result.
            """
            return FakeImageKit.FakeUploadResult()
    

@pytest.fixture
def mock_imagekit(monkeypatch):
    """
    Override the `get_imagekit` dependency with a fake ImageKit client.

    This prevents:
    - Network calls
    - Credential usage
    - External service failures

    Scope:
    - Function-level override
    """
    app.dependency_overrides[get_imagekit] = lambda: FakeImageKit()

    yield

    # Cleanup dependency overrides after test
    app.dependency_overrides.pop(get_imagekit, None)
    