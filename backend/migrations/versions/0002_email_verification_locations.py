"""email verification, pickup/return locations

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("email_verified", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column("users", sa.Column("email_code_hash", sa.String(length=64), nullable=True))
    op.add_column(
        "users", sa.Column("email_code_expires_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "users", sa.Column("email_code_sent_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "users",
        sa.Column("email_code_attempts", sa.Integer(), server_default="0", nullable=False),
    )
    # Существующие администраторы считаются подтверждёнными
    op.execute("UPDATE users SET email_verified = true WHERE role = 'admin'")

    # Для уже существующих броней — значения по умолчанию
    op.add_column(
        "bookings",
        sa.Column("pickup_location", sa.String(length=255), server_default="Офис", nullable=False),
    )
    op.add_column(
        "bookings",
        sa.Column("return_location", sa.String(length=255), server_default="Офис", nullable=False),
    )
    op.add_column(
        "bookings", sa.Column("pickup_time", sa.Time(), server_default="10:00", nullable=False)
    )
    op.add_column(
        "bookings", sa.Column("return_time", sa.Time(), server_default="10:00", nullable=False)
    )
    for column in ("pickup_location", "return_location", "pickup_time", "return_time"):
        op.alter_column("bookings", column, server_default=None)


def downgrade() -> None:
    for column in ("return_time", "pickup_time", "return_location", "pickup_location"):
        op.drop_column("bookings", column)
    for column in (
        "email_code_attempts",
        "email_code_sent_at",
        "email_code_expires_at",
        "email_code_hash",
        "email_verified",
    ):
        op.drop_column("users", column)
