import pytest
from uuid import UUID

pytestmark = pytest.mark.asyncio

# --------------------------------------------------------------------------------------
# UPLOAD TESTS
# --------------------------------------------------------------------------------------

async def test_upload_requires_auth(async_client, posts_path_v1, mock_imagekit):
    response = await async_client.post(
        f"{posts_path_v1}/upload",
            data={"caption": "Hello World"},
            files={"file": ("test.jpg", b"fake image bytes", "image/jpeg")}
    )
    assert response.status_code == 401

async def test_user_can_upload_image(async_client, posts_path_v1, auth_headers, mock_imagekit):
    # Create a post
    upload_response = await async_client.post(
        f"{posts_path_v1}/upload",
        headers=auth_headers,
        data={"caption": "Hello World"},
        files={"file": ("test.jpg", b"fake image bytes", "image/jpeg")}
    )
    assert upload_response.status_code in (200, 201)

    # Schema-level assertions
    body = upload_response.json()
    assert UUID(body["id"])
    assert body["caption"] == "Hello World"
    assert body["file_type"] == "image"
    assert body["image_url"].startswith("https://")
    assert "created_at" in body

async def test_upload_doesnot_require_caption(async_client, posts_path_v1, auth_headers, mock_imagekit):
    # Create a post
    upload_response = await async_client.post(
        f"{posts_path_v1}/upload",
        headers=auth_headers,
        files={"file": ("test.jpg", b"fake image bytes", "image/jpeg")}
    )
    assert upload_response.status_code in (200, 201)

async def test_upload_requires_file(async_client, posts_path_v1, auth_headers, mock_imagekit):
    # Create a post
    upload_response = await async_client.post(
        f"{posts_path_v1}/upload",
        headers=auth_headers,
        data={"caption": "Missing file"}
    )
    assert upload_response.status_code == 422

async def test_video_file_sets_video_type(async_client, posts_path_v1, auth_headers, mock_imagekit):
    # Create a post
    upload_response = await async_client.post(
        f"{posts_path_v1}/upload",
        headers=auth_headers,
        data={"caption": "Video post"},
        files={"file": ("video.mp4", b"fake video bytes", "video/mp4")},
    )
    assert upload_response.status_code in (200, 201)
    assert upload_response.json()["file_type"] == "video"
