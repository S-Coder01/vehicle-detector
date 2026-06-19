from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_async_session
from app.db.models import UserInfo, History
from app.core.security import get_current_user

router = APIRouter(prefix="/uploads", tags=["uploads"])

@router.get("/{user_id}/{filename}")
async def get_uploaded_image(
    user_id: int,
    filename: str,
    current_user: UserInfo = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Формируем путь с прямыми слешами для поиска в БД
    db_path = f"user_{user_id}/{filename}"
    stmt = select(History).where(
        History.user_id == user_id,
        History.image_path == db_path
    )
    result = await db.execute(stmt)
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="File not found in history")
    
    file_path = Path(f"uploads/user_{user_id}/{filename}")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)