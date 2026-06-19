from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_async_session
from app.db.models import UserInfo
from app.api.schemas.auth import User, Token
from app.core.security import get_password_hash, authenticate_user, create_jwt_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register/")
async def register_user(
    user: User,
    db: AsyncSession = Depends(get_async_session)
):
    """Регистрация нового пользователя."""
    stmt = select(UserInfo).where(UserInfo.username == user.username)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    hashed_password = get_password_hash(user.password)
    new_user = UserInfo(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "New user created", "user_id": new_user.id}

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
):
    """Аутентификация и получение JWT токена."""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_jwt_token({'sub': user.username})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_me(current_user: UserInfo = Depends(get_current_user)):
    """Получить информацию о текущем пользователе."""
    return {"id": current_user.id, "username": current_user.username}