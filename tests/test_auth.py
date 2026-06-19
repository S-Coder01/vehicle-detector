import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.db.models import UserInfo

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post(
        "/auth/register/",
        json={"username": "newuser", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "New user created"
    assert "user_id" in data

@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    # Используем пароль длиной 8 символов
    await client.post("/auth/register/", json={"username": "duplicate", "password": "pass1234"})
    response = await client.post("/auth/register/", json={"username": "duplicate", "password": "pass1234"})
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db: AsyncSession):
    username = "loginuser"
    password = "pass123"
    user = UserInfo(username=username, hashed_password=get_password_hash(password))
    db.add(user)
    await db.commit()
    response = await client.post(
        "/auth/login",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_fail(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        data={"username": "nonexistent", "password": "wrong"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"