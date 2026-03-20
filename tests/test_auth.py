import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post("/auth/register", json={
        "email": "user@test.com",
        "username": "user1",
        "password": "password123",
    })
    assert response.status_code == 201
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    payload = {"email": "user@test.com", "username": "user1", "password": "pass123"}
    await client.post("/auth/register", json=payload)
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/auth/register", json={
        "email": "user@test.com",
        "username": "user1",
        "password": "password123",
    })
    response = await client.post("/auth/login", json={
        "email": "user@test.com",
        "password": "password123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "email": "user@test.com",
        "username": "user1",
        "password": "password123",
    })
    response = await client.post("/auth/login", json={
        "email": "user@test.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(auth_client):
    response = await auth_client.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "test@test.com"


@pytest.mark.asyncio
async def test_me_unauthenticated(client):
    response = await client.get("/auth/me")
    assert response.status_code == 401