import jwt
import datetime
from typing import Optional, Dict
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_async_session
from app.db.models import UserInfo
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# Фиктивный хэш для защиты от timing-атак при несуществующем пользователе
FAKE_HASH = pwd_context.hash("")

# Схема для получения токена из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")  # URL эндпоинта логина

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля с защитой от тайм-атак через passlib"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хэширование пароля"""
    return pwd_context.hash(password)

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[UserInfo]:
    """
    Аутентификация пользователя.
    Возвращает объект UserInfo, если пароль верен, иначе None.
    Защищено от timing-атак: время выполнения одинаково для существующего и несуществующего пользователя.
    """
    # 1. Ищем пользователя в БД
    stmt = select(UserInfo).where(UserInfo.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    # 2. Всегда вызываем verify_password для защиты от timing-атак
    if user:
        password_valid = verify_password(password, user.hashed_password)
    else:
        # Для несуществующего пользователя проверяем пароль с фиктивным хэшем
        password_valid = verify_password(password, FAKE_HASH)

    # 3. Если пользователь существует, пароль верен и аккаунт активен – возвращаем
    if user and password_valid and user.is_active:
        return user
    return None

def create_jwt_token(data: Dict) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        'iat': datetime.datetime.now(datetime.UTC),
        'exp': expire,
        'sub': data.get('sub')  # username (или id)
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_session)
) -> UserInfo:
    """
    Извлекает и проверяет пользователя из JWT токена.
    Используется как зависимость в эндпоинтах, требующих авторизации.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            detail="Access Token has expired!",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Получаем пользователя из БД
    stmt = select(UserInfo).where(UserInfo.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise credentials_exception
    return user