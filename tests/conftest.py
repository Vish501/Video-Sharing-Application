"""
Global pytest fixtures for API tests.

This file defines:
- Application lifecycle management (FastAPI lifespan)
- HTTP client setup
- Authentication helpers
- Common API paths
- External service mocking (ImageKit)

These fixtures are shared across all test modules.

**Note**: Fixture modules are imported AFTER environment bootstrap
to ensure DATABASE_URL is set before app initialization.
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

from fixtures.client import *
from fixtures.auth import *
from fixtures.paths import *
from fixtures.mocks import *
