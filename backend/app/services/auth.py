import hashlib
import hmac
import logging
import secrets
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import create_token, decode_token, hash_password, verify_password
from app.models import User
from app.schemas.auth import LoginIn, RegisterIn, TokenPair, UserUpdate
from app.services import email as email_service

logger = logging.getLogger(__name__)


def issue_tokens(user: User, settings: Settings) -> TokenPair:
    return TokenPair(
        access_token=create_token(user.id, "access", settings),
        refresh_token=create_token(user.id, "refresh", settings),
    )


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(func.lower(User.email) == email.lower()))


def _aware(value: datetime) -> datetime:
    # SQLite возвращает naive datetime, PostgreSQL — aware
    return value if value.tzinfo else value.replace(tzinfo=UTC)


def _hash_code(code: str, settings: Settings) -> str:
    return hmac.new(settings.jwt_secret.encode(), code.encode(), hashlib.sha256).hexdigest()


async def send_verification_code(db: AsyncSession, user: User, settings: Settings) -> None:
    """Генерирует новый 6-значный код, сохраняет его хэш и отправляет письмо."""
    code = f"{secrets.randbelow(1_000_000):06d}"
    now = datetime.now(UTC)
    user.email_code_hash = _hash_code(code, settings)
    user.email_code_expires_at = now + timedelta(minutes=settings.email_code_ttl_min)
    user.email_code_sent_at = now
    user.email_code_attempts = 0
    await db.commit()

    body = (
        f"Здравствуйте, {user.full_name}!\n\n"
        f"Ваш код подтверждения email на сайте Joker Auto Rent: {code}\n"
        f"Код действует {settings.email_code_ttl_min} минут.\n\n"
        "Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо."
    )
    try:
        await email_service.send_email(settings, user.email, "Код подтверждения email", body)
    except Exception:
        # Регистрация не должна падать из-за почты — пользователь запросит код повторно
        logger.exception("Failed to send verification email to %s", user.email)


async def register(db: AsyncSession, data: RegisterIn, settings: Settings) -> TokenPair:
    if await get_user_by_email(db, data.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "Пользователь с таким email уже существует")
    user = User(
        email=data.email.lower(),
        phone=data.phone,
        full_name=data.full_name.strip(),
        password_hash=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await send_verification_code(db, user, settings)
    return issue_tokens(user, settings)


async def verify_email(db: AsyncSession, user: User, code: str, settings: Settings) -> User:
    if user.email_verified:
        return user
    if user.email_code_hash is None or user.email_code_expires_at is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Запросите новый код подтверждения")
    if _aware(user.email_code_expires_at) < datetime.now(UTC):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Код истёк, запросите новый")
    if user.email_code_attempts >= settings.email_code_max_attempts:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS, "Слишком много попыток, запросите новый код"
        )
    if not hmac.compare_digest(user.email_code_hash, _hash_code(code, settings)):
        user.email_code_attempts += 1
        await db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Неверный код")

    user.email_verified = True
    user.email_code_hash = None
    user.email_code_expires_at = None
    user.email_code_attempts = 0
    await db.commit()
    return user


async def resend_verification(db: AsyncSession, user: User, settings: Settings) -> None:
    if user.email_verified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email уже подтверждён")
    if user.email_code_sent_at is not None:
        elapsed = (datetime.now(UTC) - _aware(user.email_code_sent_at)).total_seconds()
        wait = int(settings.email_resend_cooldown_sec - elapsed)
        if wait > 0:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS,
                f"Отправить код повторно можно через {wait} сек.",
            )
    await send_verification_code(db, user, settings)


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


async def update_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(user, field, value)
    await db.commit()
    return user
