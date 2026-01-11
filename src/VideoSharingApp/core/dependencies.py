import os
from dotenv import load_dotenv
from fastapi import Request
from pathlib import Path

from VideoSharingApp.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

def get_imagekit(requests: Request):
    """
    Dependency to safely retrieve ImageKit client.
    """
    imagekit = getattr(requests.app.state, "imagekit", None)

    if imagekit is None:
        raise RuntimeError("ImageKit client was not found in application state.")
    
    return imagekit

def get_database_url() -> str:
    """
    Resolve and validate the database URL.

    - Ensures SQLite directories exist
    - Fails fast if configuration is invalid
    """
    database_dir  = os.getenv("DATABASE_DIR", "./artifacts/database")
    database_name = os.getenv("DATABASE_NAME", "app.db")

    # Validate database directory
    if not database_dir or not database_dir.strip():
        raise RuntimeError("DATABASE_DIR  cannot be empty. Check environment configurations.")
    
    # Validate database name
    if not database_name or not database_name.strip():
        raise RuntimeError("DATABASE_NAME cannot be empty. Check environment configurations.")

    if not database_name.endswith(".db"):
        raise RuntimeError("DATABASE_NAME  needs to be suffixed with `.db`. Check environment configurations.")

    # Ensure database directory exists
    try:
        Path(database_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.exception(f"Failed to create database directory: %s", database_dir)
        raise RuntimeError(
            f"Unable to initialize database directory: {database_dir}"
        ) from e

    # If DATABASE_URL is explicitly provided, it takes precedence.
    # Otherwise, default to an async SQLite database.
    database_url = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{database_dir}/{database_name}"
    )
    
    # In case of improper DATABASE_URL loaded from .env
    if not database_url.strip():
        raise RuntimeError("DATABASE_URL cannot be empty. Check environment file.")
    
    return database_url
