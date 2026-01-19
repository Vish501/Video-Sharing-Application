"""
Feed API tests.

Note:
- Feed is global (not user-specific)
- Requires authentication
"""

import pytest
import asyncio

pytestmark = pytest.mark.asyncio

# --------------------------------------------------------------------------------------
# AUTH TESTS
# --------------------------------------------------------------------------------------

async def test_feed_requires_auth(async_client, feed_path_v1, auth_headers):
    response = await async_client.get(feed_path_v1)
    assert response.status_code == 401

# --------------------------------------------------------------------------------------
# EMPTY FEED TESTS
# --------------------------------------------------------------------------------------

async def test_empty_feed_returns_empty_list(async_client, auth_headers, feed_path_v1):
    # Get Auth Headers (Register and Login)
    headers = auth_headers
    
    feed_response = await async_client.get(
        feed_path_v1,
        headers=headers
    )

    assert feed_response.status_code == 200
    body = feed_response.json()
    
    assert "posts" in body
    assert body["posts"] == []

# --------------------------------------------------------------------------------------
# FEED CONTENT TESTS
# --------------------------------------------------------------------------------------

async def test_feed_returns_posts_with_expected_fields(async_client, auth_headers, feed_path_v1, posts_path_v1, mock_imagekit):
    # Get Auth Headers (Register and Login)
    headers = auth_headers

    # Create a post
    upload_response = await async_client.post(
        f"{posts_path_v1}/upload",
        headers=headers,
        data={"caption": "Hello World"},
        files={"file": ("test.jpg", b"fake image bytes", "image/jpeg")}
    )
    assert upload_response.status_code in (200, 201)

    # Fetch feed
    feed_response = await async_client.get(
        feed_path_v1,
        headers=headers
    )
    assert feed_response.status_code == 200

    posts = feed_response.json()["posts"]
    assert len(posts) == 1

    post = posts[0]

    # Structural assertion
    assert post["caption"] == "Hello World"
    assert post["is_owner"] is True

    # Required keys
    for key in (
        "id",
        "user_id",
        "url",
        "file_name",
        "file_type",
        "created_at",
    ):
        assert key in post

# --------------------------------------------------------------------------------------
# ORDERING TESTS
# --------------------------------------------------------------------------------------

async def test_feed_is_ordered_by_created_at_desc(async_client, auth_headers, feed_path_v1, posts_path_v1, mock_imagekit):
    # Get Auth Headers (Register and Login)
    headers = auth_headers

    # Create two posts
    for caption in ["first post", "second post"]:
        upload_response = await async_client.post(
            f"{posts_path_v1}/upload",
            headers=headers,
            data={"caption": caption},
            files={"file": ("test.jpg", b"fake image bytes", "image/jpeg")}
        )
        assert upload_response.status_code in (200, 201)

        if caption == "first post":
            # Due to conflict with how time is commuted at storage
            await asyncio.sleep(1.1) 

    # Fetch feed
    feed_response = await async_client.get(
        feed_path_v1,
        headers=headers
    )
    assert feed_response.status_code == 200

    posts = feed_response.json()["posts"]
    assert len(posts) == 2
    assert posts[0]["caption"] == "second post"
    assert posts[1]["caption"] == "first post"
    assert posts[0]["created_at"] > posts[1]["created_at"]

    # Required keys
    for post in posts:
        for key in (
            "id",
            "user_id",
            "url",
            "file_name",
            "file_type",
            "created_at",
        ):
            assert key in post
