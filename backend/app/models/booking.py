from datetime import UTC, date, datetime, time
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Time,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, str_enum
from app.models.car import Car
from app.models.user import User


class BookingStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


BLOCKING_STATUSES = (BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.ACTIVE)


class Booking(Base):
    """Бронь на полуоткрытый интервал [start_date, end_date): в день возврата авто свободно."""

    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("end_date > start_date", name="dates_order"),
        Index("ix_bookings_car_dates", "car_id", "start_date", "end_date"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    car_id: Mapped[int] = mapped_column(ForeignKey("cars.id", ondelete="RESTRICT"))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    pickup_location: Mapped[str] = mapped_column(String(255))
    return_location: Mapped[str] = mapped_column(String(255))
    pickup_time: Mapped[time] = mapped_column(Time)
    return_time: Mapped[time] = mapped_column(Time)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[BookingStatus] = mapped_column(
        str_enum(BookingStatus, "booking_status"), default=BookingStatus.PENDING, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), server_default=func.now()
    )

    car: Mapped[Car] = relationship(lazy="selectin")
    user: Mapped[User] = relationship(lazy="selectin")

    @property
    def days(self) -> int:
        return (self.end_date - self.start_date).days
