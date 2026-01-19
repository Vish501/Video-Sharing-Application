""" 
Note:
Logout is not tested because JWT authentication is stateless.
Token invalidation (blacklisting / rotation) is not implemented.
Logout is handled client-side by deleting the token.
"""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

# --------------------------------------------------------------------------------------
# REGISTRATION TESTS
# --------------------------------------------------------------------------------------

async def test_user_can_register(register_user_v1, test_user):
    """
    Ensure a new user can successfully register.
    """
    reg_response = await register_user_v1(test_user)
    assert reg_response.status_code == 201
    
    body = reg_response.json()
    assert body["email"] == test_user["email"]
    assert "id" in body

async def test_duplicate_registration_fails(register_user_v1, test_user):
    first_response  = await register_user_v1(test_user)
    assert first_response.status_code == 201

    second_response  = await register_user_v1(test_user)
    assert second_response.status_code == 400

async def test_register_missing_email_fails(register_user_v1, test_user):
    payload = {"password": test_user["password"]}
    reg_response = await register_user_v1(payload)
    assert reg_response.status_code == 422

async def test_register_missing_password_fails(register_user_v1, test_user):
    payload = {"email": test_user["email"]}
    reg_response = await register_user_v1(payload)
    assert reg_response.status_code == 422

# --------------------------------------------------------------------------------------
# LOGIN TESTS
# --------------------------------------------------------------------------------------

async def test_user_can_login_and_get_jwt(register_user_v1, login_user_v1, test_user):
    # Register
    reg_response = await register_user_v1(test_user)
    assert reg_response.status_code == 201

    # Login
    login_response = await login_user_v1(
        test_user["email"],
        test_user["password"]
    )

    assert login_response.status_code == 200

    body = login_response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

async def test_login_with_wrong_credentials_fails(login_user_v1):
    payload = {
        "email": "wrong@example.com",
        "password": "invalidpassword123@",
    }

    # Login
    login_response = await login_user_v1(
        payload["email"],
        payload["password"]
    )

    assert login_response.status_code in (400, 401)

# --------------------------------------------------------------------------------------
# USER TESTS
# --------------------------------------------------------------------------------------

async def test_users_me_requires_auth(async_client, users_path_v1):
    response = await async_client.get(users_path_v1) 
    assert response.status_code == 401


async def test_users_me_with_valid_token(async_client, register_user_v1, login_user_v1, test_user, users_path_v1):
    # Register
    reg_response = await register_user_v1(test_user)
    assert reg_response.status_code == 201

    # Login
    login_response = await login_user_v1(
        test_user["email"],
        test_user["password"]
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    response = await async_client.get(
        users_path_v1,
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()

    assert body["email"] == test_user["email"]

async def test_users_me_with_invalid_token(async_client, users_path_v1):
    response = await async_client.get(
        users_path_v1,
        headers={"Authorization": "Bearer malformedtoken123"}
    )

    assert response.status_code == 401
    