import pytest

pytestmark = pytest.mark.asyncio

# --------------------------------------------------------------------------------------
# DELETE TESTS
# --------------------------------------------------------------------------------------

async def test_user_can_delete_own_post(async_client, auth_headers, posts_path_v1, mock_imagekit):
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

    post_id = upload_response.json()["id"]

    # Delete Post
    delete_response = await async_client.delete(
        f"{posts_path_v1}/{post_id}",
        headers=headers,
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {"success": True}


async def test_cannot_delete_post_without_auth(async_client, auth_headers, posts_path_v1, feed_path_v1, mock_imagekit):
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

    post_id = upload_response.json()["id"]

    # Delete Post
    delete_response = await async_client.delete(
        f"{posts_path_v1}/{post_id}",
    )

    assert delete_response.status_code == 401

    # Check feed
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

    for key in (
        "id",
        "user_id",
        "url",
        "file_name",
        "file_type",
        "created_at",
    ):
        assert key in post


async def test_delete_invalid_post_id(async_client, auth_headers, posts_path_v1, mock_imagekit):
    response = await async_client.delete(
        f"{posts_path_v1}/not-a-uuid",
        headers=auth_headers,
    )

    assert response.status_code == 400

async def test_delete_without_valid_id(async_client, auth_headers, posts_path_v1, feed_path_v1, mock_imagekit):
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

    # Test ID
    post_id = "00000000-0000-0000-0000-000000000000"

    # Delete Post
    delete_response = await async_client.delete(
        f"{posts_path_v1}/{post_id}",
        headers=headers,
    )

    assert delete_response.status_code == 404

    # Check feed
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

    for key in (
        "id",
        "user_id",
        "url",
        "file_name",
        "file_type",
        "created_at",
    ):
        assert key in post

async def test_user_cannot_delete_others_post(async_client, auth_user, posts_path_v1, mock_imagekit):
# Get Auth Headers (Register and Login)
    user1_headers = await auth_user()
    user2_headers = await auth_user()

    # Create a post
    upload_response = await async_client.post(
        f"{posts_path_v1}/upload",
        headers=user1_headers,
        data={"caption": "Hello World"},
        files={"file": ("test.jpg", b"fake image bytes", "image/jpeg")}
    )

    assert upload_response.status_code in (200, 201)

    post_id = upload_response.json()["id"]

    # Delete Post
    delete_response = await async_client.delete(
        f"{posts_path_v1}/{post_id}",
        headers=user2_headers,
    )

    assert delete_response.status_code == 403
