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
    # Directory where the database file will be stored.
    database_dir  = os.getenv("DATABASE_DIR", "./artifacts/database/test.db")

    # In case of improper DATABASE_DIR loaded from .env
    if not database_dir.strip():
        raise RuntimeError("Database directory cannot be empty. Check environment file.")

    # Ensure the database directory exists before the application starts.
    try:
        Path(database_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:
        logger.exception(f"Failed to create database directory: {database_dir}")
        raise RuntimeError(f"Unable to initialize database directory: {database_dir}") from e

    # If DATABASE_URL is explicitly provided, it takes precedence.
    # Otherwise, default to an async SQLite database stored in DATABASE_DIR.
    database_url = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{database_dir}/app.db"
        )
    
    # In case of improper DATABASE_URL loaded from .env
    if not database_url.strip():
        raise RuntimeError("Database url cannot be empty. Check environment file.")
    
    return database_url
