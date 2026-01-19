import pytest
from httpx import AsyncClient
from fastapi import status

# Run async tests
pytestmark = pytest.mark.asyncio

async def test_health_endpoint_returns_200(async_client: AsyncClient):
    """
    Basic liveness check.
    Ensures the service is up and responding.
    """
    response = await async_client.get("/health")

    assert response.status_code == status.HTTP_200_OK

async def test_health_endpoint_response_schema(async_client: AsyncClient):
    """
    Validates the response payload structure returned from the ./health endpoint.
    """
    response = await async_client.get("/health")

    data = response.json()

    assert isinstance(data, dict)
    assert "ok" in data
    assert data["ok"] == True

async def test_health_endpoint_is_fast(async_client: AsyncClient):
    """
    Guards against blocking calls
    """
    response = await async_client.get("/health")

    assert response.elapsed.total_seconds() < 0.5
    