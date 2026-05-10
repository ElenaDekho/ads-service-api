import bcrypt
import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, Header, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from models import User, Token
from database import get_db_session


def hash_password(password: str) -> str:
    """Хэширует пароль с помощью bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def check_password(password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли пароль хэшу"""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def generate_token() -> str:
    """Генерирует уникальный токен"""
    return str(uuid.uuid4())


async def create_token(
        db_session: AsyncSession,
        user_id: int,
        ttl_hours: int = 48
) -> Token:
    """Создаёт новый токен для пользователя"""
    token_value = generate_token()
    expires_at = datetime.now() + timedelta(hours=ttl_hours)

    new_token = Token(
        token=token_value,
        user_id=user_id,
        expires_at=expires_at
    )
    db_session.add(new_token)
    await db_session.commit()
    await db_session.refresh(new_token)
    return new_token


async def get_current_user(
        token: str = Header(..., alias="x-token"),
        db_session: AsyncSession = Depends(get_db_session)
) -> User:
    """Получает текущего пользователя по токену из заголовка x-token"""
    # Ищем токен в БД
    stmt = select(Token).where(Token.token == token)
    token_obj = await db_session.scalar(stmt)

    if not token_obj:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Проверяем, не истёк ли токен (48 часов)
    if token_obj.expires_at < datetime.now().astimezone():
        raise HTTPException(status_code=401, detail="Token expired")

    # Получаем пользователя
    stmt = select(User).where(User.id == token_obj.user_id)
    user = await db_session.scalar(stmt)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user