from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, str_enum


class Transmission(StrEnum):
    AUTOMATIC = "automatic"
    MANUAL = "manual"


class Fuel(StrEnum):
    PETROL = "petrol"
    DIESEL = "diesel"
    HYBRID = "hybrid"
    ELECTRIC = "electric"
    GAS = "gas"


class CarCategory(Base):
    __tablename__ = "car_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)


class Car(Base):
    __tablename__ = "cars"

    id: Mapped[int] = mapped_column(primary_key=True)
    brand: Mapped[str] = mapped_column(String(64))
    model: Mapped[str] = mapped_column(String(64))
    year: Mapped[int] = mapped_column(SmallInteger)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("car_categories.id", ondelete="RESTRICT"), index=True
    )
    transmission: Mapped[Transmission] = mapped_column(str_enum(Transmission, "transmission"))
    fuel: Mapped[Fuel] = mapped_column(str_enum(Fuel, "fuel"))
    seats: Mapped[int] = mapped_column(SmallInteger)
    price_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    deposit: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    description: Mapped[str] = mapped_column(Text, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )

    category: Mapped[CarCategory] = relationship(lazy="selectin")
    images: Mapped[list["CarImage"]] = relationship(
        lazy="selectin",
        order_by="CarImage.sort_order",
        cascade="all, delete-orphan",
        back_populates="car",
    )


class CarImage(Base):
    __tablename__ = "car_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(String(512))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    car: Mapped[Car] = relationship(back_populates="images")
