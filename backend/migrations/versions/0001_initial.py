"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-10-22
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _enum(name: str, *values: str) -> sa.Enum:
    return sa.Enum(*values, name=name, native_enum=False, length=16)


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", _enum("user_role", "client", "admin"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
    )

    op.create_table(
        "car_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_car_categories")),
        sa.UniqueConstraint("name", name=op.f("uq_car_categories_name")),
    )

    op.create_table(
        "cars",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(length=64), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("year", sa.SmallInteger(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("transmission", _enum("transmission", "automatic", "manual"), nullable=False),
        sa.Column(
            "fuel", _enum("fuel", "petrol", "diesel", "hybrid", "electric", "gas"), nullable=False
        ),
        sa.Column("seats", sa.SmallInteger(), nullable=False),
        sa.Column("price_per_day", sa.Numeric(10, 2), nullable=False),
        sa.Column("deposit", sa.Numeric(10, 2), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["car_categories.id"],
            name=op.f("fk_cars_category_id_car_categories"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_cars")),
    )
    op.create_index(op.f("ix_cars_category_id"), "cars", ["category_id"])

    op.create_table(
        "car_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=512), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["car_id"], ["cars.id"], name=op.f("fk_car_images_car_id_cars"), ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_car_images")),
    )
    op.create_index(op.f("ix_car_images_car_id"), "car_images", ["car_id"])

    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("car_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("total_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("payment_method", _enum("payment_method", "cash", "online"), nullable=False),
        sa.Column(
            "status",
            _enum("booking_status", "pending", "confirmed", "active", "completed", "cancelled"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("end_date > start_date", name=op.f("ck_bookings_dates_order")),
        sa.ForeignKeyConstraint(
            ["car_id"], ["cars.id"], name=op.f("fk_bookings_car_id_cars"), ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name=op.f("fk_bookings_user_id_users"), ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bookings")),
    )
    op.create_index("ix_bookings_car_dates", "bookings", ["car_id", "start_date", "end_date"])
    op.create_index(op.f("ix_bookings_user_id"), "bookings", ["user_id"])
    op.create_index(op.f("ix_bookings_status"), "bookings", ["status"])

    # Запрет пересечения активных броней одного авто на уровне БД.
    # Интервал [start_date, end_date) — день возврата свободен для следующей брони.
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        """
        ALTER TABLE bookings ADD CONSTRAINT ex_bookings_car_no_overlap
        EXCLUDE USING gist (car_id WITH =, daterange(start_date, end_date, '[)') WITH &&)
        WHERE (status IN ('pending', 'confirmed', 'active'))
        """
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


def downgrade() -> None:
    op.drop_table("payments")
    op.drop_table("bookings")
    op.drop_table("car_images")
    op.drop_table("cars")
    op.drop_table("car_categories")
    op.drop_table("users")
