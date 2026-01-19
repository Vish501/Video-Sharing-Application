"""
FakeImageKit, mock_imagekit
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
    