from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, Integer, String, false, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, str_enum


class UserRole(StrEnum):
    CLIENT = "client"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(32))
    full_name: Mapped[str] = mapped_column(String(255))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(str_enum(UserRole, "user_role"), default=UserRole.CLIENT)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )

    # Подтверждение email одноразовым кодом (храним только хэш)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    email_code_hash: Mapped[str | None] = mapped_column(String(64))
    email_code_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    email_code_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    email_code_attempts: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
