"""
Tests for core dependencies.

Note on Intentional Exclusions:
-------------------------------
The `get_imagekit` dependency is intentionally NOT unit-tested here.

Reasons:
- It is a thin wrapper around a third-party SDK
- Behavior depends entirely on external configuration and network calls
- Unit-testing would require deep mocking with low confidence return

Coverage is instead achieved indirectly through:
- API route tests (e.g. POST /posts/upload)
- Runtime validation in non-production environments

If ImageKit logic becomes non-trivial (custom retries, transforms,
fallback logic, etc.), unit tests should be added at that point.

This aligns with FastAPI's recommended testing strategy:
test dependency wiring through route behavior, not direct invocation.
"""

import pytest
from VideoSharingApp.core.dependencies import get_database_url

def test_returns_database_url_when_explicit_url_is_set(tmp_path, monkeypatch):
    db_url = "postgresql+asyncpg://user:pass@localhost:5432/appdb"

    # Set mocked env variables
    monkeypatch.setenv("DATABASE_URL", str(db_url))

    # Construct URL using the function
    sql_url = get_database_url()

    assert sql_url == db_url


def test_creates_sqlite_directory_if_missing(tmp_path, monkeypatch):
    """
    If DATABASE_URL is not set, the function should:
    - Create the database directory if it does not exist
    - Return a valid sqlite+aiosqlite url
    """
    db_dir = tmp_path / "sqlite_db"
    db_name = "test.db"

    # Precondition: directory does not exist
    assert not db_dir.exists()

    # Set mocked env variables
    monkeypatch.setenv("DATABASE_DIR", str(db_dir))
    monkeypatch.setenv("DATABASE_NAME", str(db_name))
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Construct URL using the function
    sql_url = get_database_url()

    # Postconditions
    assert db_dir.exists()
    assert sql_url == f"sqlite+aiosqlite:///{db_dir}/{db_name}"


def test_existing_sqlite_directory_is_reused(tmp_path, monkeypatch):
    db_dir = tmp_path / "existing_db"
    db_name = "test.db"

    # Precondition
    db_dir.mkdir()

    # Set mocked env variables
    monkeypatch.setenv("DATABASE_DIR", str(db_dir))
    monkeypatch.setenv("DATABASE_NAME", str(db_name))
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Construct URL using the function
    sql_url = get_database_url()

    assert db_dir.exists()
    assert sql_url == f"sqlite+aiosqlite:///{db_dir}/{db_name}"


def test_database_url_env_var_takes_precedence(tmp_path, monkeypatch):
    db_dir = tmp_path / "sqlite_db"
    db_name = "test.db"
    db_url = f"sqlite+aiosqlite:///{db_dir}/test/{db_name}"

    # Precondition
    db_dir.mkdir()
    assert db_dir.exists()

    # Set mocked env variables
    monkeypatch.setenv("DATABASE_DIR", str(db_dir))
    monkeypatch.setenv("DATABASE_NAME", str(db_name))
    monkeypatch.setenv("DATABASE_URL", str(db_url))

    # Construct URL using the function
    sql_url = get_database_url()

    assert db_dir.exists()
    assert sql_url != f"sqlite+aiosqlite:///{db_dir}/{db_name}"
    assert sql_url == db_url


def test_raises_error_when_db_name_empty(tmp_path, monkeypatch):
    db_dir = tmp_path / "sqlite_db"
    db_name = " "

    # Set mocked env variables
    monkeypatch.setenv("DATABASE_DIR", str(db_dir))
    monkeypatch.setenv("DATABASE_NAME", str(db_name))
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Match error
    with pytest.raises(RuntimeError, match="DATABASE_NAME cannot be empty. Check environment configurations."):
        get_database_url()


def test_raises_error_when_db_dir_empty(monkeypatch):
    db_dir = " "
    db_name = "test.db"

    # Set mocked env variables
    monkeypatch.setenv("DATABASE_DIR", str(db_dir))
    monkeypatch.setenv("DATABASE_NAME", str(db_name))
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Match error
    with pytest.raises(RuntimeError, match="DATABASE_DIR cannot be empty. Check environment configurations."):
        get_database_url()


def test_raises_error_when_db_url_empty(tmp_path, monkeypatch):
    db_dir = tmp_path / "sqlite_db"
    db_name = "test.db"
    db_url = " "

    # Set mocked env variables
    monkeypatch.setenv("DATABASE_DIR", str(db_dir))
    monkeypatch.setenv("DATABASE_NAME", str(db_name))
    monkeypatch.setenv("DATABASE_URL", str(db_url))

    # Match error
    with pytest.raises(RuntimeError, match="DATABASE_URL cannot be empty. Check environment file."):
        get_database_url()


def test_raises_error_when_db_name_incomplete(tmp_path, monkeypatch):
    db_dir = tmp_path / "sqlite_db"
    db_name = "test"

    # Set mocked env variables
    monkeypatch.setenv("DATABASE_DIR", str(db_dir))
    monkeypatch.setenv("DATABASE_NAME", str(db_name))
    monkeypatch.delenv("DATABASE_URL", raising=False)

    # Match error
    with pytest.raises(RuntimeError, match="DATABASE_NAME needs to be suffixed with `.db`. Check environment configurations."):
        get_database_url()
