"""
auth_user, login_user_v1, register_user_v1
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
