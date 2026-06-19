from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, desc

from app.db.database import get_async_session
from app.db.models import UserInfo, History
from app.core.security import get_current_user
from app.services import storage
from app.api.schemas.history import HistoryEntry, HistoryListResponse

router = APIRouter(prefix="/history", tags=["history"])

@router.get("/", response_model=HistoryListResponse)
async def get_history(
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Получить историю текущего пользователя."""
    stmt = (
        select(History)
        .where(History.user_id == current_user.id)
        .order_by(desc(History.created_at))
    )
    result = await db.execute(stmt)
    entries = result.scalars().all()

    items = [
        HistoryEntry(
            id=entry.id,
            image_path=entry.image_path,
            model_used=entry.model_used,
            created_at=entry.created_at,
            results_json=entry.results_json  # добавляем JSON строку
        )
        for entry in entries
    ]
    return HistoryListResponse(entries=items, total=len(items))

@router.delete("/{entry_id}")
async def delete_history_entry(
    entry_id: int,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Удалить конкретную запись истории."""
    stmt = select(History).where(
        History.id == entry_id,
        History.user_id == current_user.id
    )
    result = await db.execute(stmt)
    entry = result.scalar_one_or_none()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись не найдена"
        )

    storage.delete_file(entry.image_path)
    await db.delete(entry)
    await db.commit()
    return {"message": "Запись удалена"}

@router.delete("/")
async def clear_history(
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Очистить всю историю текущего пользователя."""
    stmt = select(History).where(History.user_id == current_user.id)
    result = await db.execute(stmt)
    entries = result.scalars().all()

    for entry in entries:
        storage.delete_file(entry.image_path)

    await db.execute(delete(History).where(History.user_id == current_user.id))
    await db.commit()
    return {"message": "История очищена"}