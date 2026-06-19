import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

from app.db.database import Base, get_async_session
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.models import UserInfo
from main import app

# Тестовая БД (создайте её заранее)
TEST_DATABASE_URL = "postgresql+asyncpg://test_user:test_pass@localhost/test_vehicle_detector_db"

# Движок с NullPool – каждое соединение создаётся заново, избегаем конфликтов
engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestingSessionLocal = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

# Переопределяем зависимость FastAPI на тестовую сессию
async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

@pytest.fixture(scope="session", autouse=True)
async def setup_test_db():
    """Создаёт таблицы один раз перед всеми тестами."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function", autouse=True)
async def clean_db():
    """Очищает все таблицы перед каждым тестом через отдельное соединение."""
    async with engine_test.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f"TRUNCATE TABLE {table.name} CASCADE"))

@pytest.fixture(scope="function")
def event_loop():
    """Создаёт новый цикл событий для каждого теста (решает проблемы с asyncpg)."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP клиент для тестирования эндпоинтов."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Сессия БД для тестов (для прямых запросов)."""
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="function")
async def auth_token(client: AsyncClient, db: AsyncSession) -> str:
    """
    Создаёт тестового пользователя и возвращает JWT-токен.
    Используется в тестах, требующих авторизации.
    """
    username = "testuser2"
    password = "testpass123"
    user = UserInfo(username=username, hashed_password=get_password_hash(password))
    db.add(user)
    await db.commit()

    # Логинимся через эндпоинт /auth/login
    response = await client.post(
        "/auth/login",
        data={"username": username, "password": password}
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]