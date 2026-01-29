from fastapi import APIRouter
from VideoSharingApp.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["health"])

@router.get("/health")
async def health() -> dict[str, bool]:
    """
    Health check endpoint to test if application is running
    """
    logger.info("health_check_passed")
    return {"ok": True}
