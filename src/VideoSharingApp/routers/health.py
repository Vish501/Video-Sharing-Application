from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
async def health() -> dict[str, bool]:
    """
    Health check endpoint to test if application is running
    """
    return {"ok": True}
