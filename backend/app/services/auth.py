from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import create_token, decode_token, verify_password
from app.models import User
from app.schemas.auth import LoginIn, TokenPair


def issue_tokens(user: User, settings: Settings) -> TokenPair:
    return TokenPair(
        access_token=create_token(user.id, "access", settings),
        refresh_token=create_token(user.id, "refresh", settings),
    )


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(func.lower(User.email) == email.lower()))


async def login(db: AsyncSession, data: LoginIn, settings: Settings) -> TokenPair:
    user = await get_user_by_email(db, data.email)
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Неверный email или пароль")
    return issue_tokens(user, settings)


async def refresh(db: AsyncSession, refresh_token: str, settings: Settings) -> TokenPair:
    user_id = decode_token(refresh_token, "refresh", settings)
    user = await db.get(User, user_id) if user_id is not None else None
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Сессия истекла, войдите снова")
    return issue_tokens(user, settings)
