"""remove payments: bookings are confirmed via WhatsApp

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-24
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _enum(name: str, *values: str) -> sa.Enum:
    return sa.Enum(*values, name=name, native_enum=False, length=16)


def upgrade() -> None:
    op.drop_index(op.f("ix_payments_booking_id"), table_name="payments")
    op.drop_table("payments")
    with op.batch_alter_table("bookings") as batch:
        batch.drop_column("payment_method")


def downgrade() -> None:
    with op.batch_alter_table("bookings") as batch:
        batch.add_column(
            sa.Column(
                "payment_method",
                _enum("payment_method", "cash", "online"),
                server_default="cash",
                nullable=False,
            )
        )
    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("provider_payment_id", sa.String(length=128), nullable=False),
        sa.Column(
            "status",
            _enum("payment_status", "pending", "succeeded", "failed", "refunded"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["booking_id"],
            ["bookings.id"],
            name=op.f("fk_payments_booking_id_bookings"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_payments")),
        sa.UniqueConstraint(
            "provider", "provider_payment_id", name=op.f("uq_payments_provider")
        ),
    )
    op.create_index(op.f("ix_payments_booking_id"), "payments", ["booking_id"])
