from datetime import UTC, datetime, timedelta
from typing import Literal

import jwt
from passlib.context import CryptContext

from app.core.config import Settings

TokenType = Literal["access", "refresh"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(user_id: int, token_type: TokenType, settings: Settings) -> str:
    if token_type == "access":
        ttl = timedelta(minutes=settings.jwt_access_ttl_min)
    else:
        ttl = timedelta(days=settings.jwt_refresh_ttl_days)
    now = datetime.now(UTC)
    payload = {"sub": str(user_id), "type": token_type, "iat": now, "exp": now + ttl}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str, expected_type: TokenType, settings: Settings) -> int | None:
    """Возвращает id пользователя или None, если токен невалиден."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    try:
        return int(payload["sub"])
    except (KeyError, ValueError):
        return None
