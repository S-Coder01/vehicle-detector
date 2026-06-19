import pytest
from unittest.mock import patch
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import History, UserInfo

@pytest.mark.asyncio
async def test_get_history_empty(client: AsyncClient, auth_token):
    response = await client.get(
        "/history/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["entries"] == []

@pytest.mark.asyncio
async def test_get_history_with_entries(client: AsyncClient, auth_token, db: AsyncSession):
    stmt = select(UserInfo).where(UserInfo.username == "testuser2")
    result = await db.execute(stmt)
    user = result.scalar_one()
    for i in range(2):
        entry = History(
            user_id=user.id,
            image_path=f"test/path_{i}.jpg",
            model_used="yolo26n_fast",
            results_json='{"detections": []}'
        )
        db.add(entry)
    await db.commit()

    response = await client.get(
        "/history/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["entries"]) == 2

@pytest.mark.asyncio
@patch("app.services.storage.delete_file")  # правильный путь
async def test_delete_entry(mock_delete, client: AsyncClient, auth_token, db: AsyncSession):
    stmt = select(UserInfo).where(UserInfo.username == "testuser2")
    result = await db.execute(stmt)
    user = result.scalar_one()
    entry = History(
        user_id=user.id,
        image_path="test/path.jpg",
        model_used="yolo26n_fast",
        results_json='{}'
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    entry_id = entry.id

    response = await client.delete(
        f"/history/{entry_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Запись удалена"
    mock_delete.assert_called_once_with("test/path.jpg")

@pytest.mark.asyncio
async def test_delete_nonexistent_entry(client: AsyncClient, auth_token):
    response = await client.delete(
        "/history/9999",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Запись не найдена"

@pytest.mark.asyncio
@patch("app.services.storage.delete_file")
async def test_clear_history(mock_delete, client: AsyncClient, auth_token, db: AsyncSession):
    stmt = select(UserInfo).where(UserInfo.username == "testuser2")
    result = await db.execute(stmt)
    user = result.scalar_one()
    for i in range(2):
        entry = History(
            user_id=user.id,
            image_path=f"test/path_{i}.jpg",
            model_used="yolo26n_fast",
            results_json='{}'
        )
        db.add(entry)
    await db.commit()

    response = await client.delete(
        "/history/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "История очищена"
    assert mock_delete.call_count == 2