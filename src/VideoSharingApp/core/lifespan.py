from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from VideoSharingApp.database import create_db_and_tables, close_engine
from VideoSharingApp.images import create_imagekit_client
from VideoSharingApp.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown logic.
    Fails fast if critical dependencies are misconfigured.

    Initializes:
    - Database tables
    - ImageKit client

    Closes:
    - Engine
    """
    try:
        logger.info("Starting application startup sequence.")

        await create_db_and_tables()
        logger.info("Database tables initialized successfully.")

        app.state.imagekit = create_imagekit_client()
        logger.info("ImageKit client initialized successfully.")

        yield

        await close_engine()
        logger.info("Engine closed.")

    except Exception as e:
        logger.critical(
            "Application startup failed. Shutting down.",
            exc_info=True,
        )
        raise

    finally:
        logger.info("Application shutdown sequence complete.")
        