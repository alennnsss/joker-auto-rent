from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models import Booking, BookingStatus, User
from app.services.cars import overlap_clause

# Допустимые смены статуса администратором
ADMIN_TRANSITIONS: dict[BookingStatus, set[BookingStatus]] = {
    BookingStatus.PENDING: {BookingStatus.CONFIRMED, BookingStatus.CANCELLED},
    BookingStatus.CONFIRMED: {BookingStatus.ACTIVE, BookingStatus.CANCELLED},
    BookingStatus.ACTIVE: {BookingStatus.COMPLETED},
    BookingStatus.COMPLETED: set(),
    BookingStatus.CANCELLED: set(),
}


def today(settings: Settings) -> date:
    return datetime.now(ZoneInfo(settings.timezone)).date()


def calculate_price(price_per_day: Decimal, start: date, end: date) -> Decimal:
    days = (end - start).days
    return (price_per_day * days).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


async def is_car_available(db: AsyncSession, car_id: int, start: date, end: date) -> bool:
    busy = await db.scalar(
        select(exists().where(Booking.car_id == car_id, *overlap_clause(start, end)))
    )
    return not busy


async def get_booking(db: AsyncSession, booking_id: int, user: User | None = None) -> Booking:
    """Загружает бронь со всеми связями. Если передан user — проверяет владельца."""
    booking = await db.scalar(
        select(Booking).where(Booking.id == booking_id).execution_options(populate_existing=True)
    )
    if booking is None or (user is not None and booking.user_id != user.id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Бронирование не найдено")
    return booking


async def list_all_bookings(
    db: AsyncSession, status_filter: BookingStatus | None, limit: int, offset: int
) -> list[Booking]:
    stmt = select(Booking).order_by(Booking.id.desc()).limit(limit).offset(offset)
    if status_filter is not None:
        stmt = stmt.where(Booking.status == status_filter)
    return list(await db.scalars(stmt))


async def _cancel(db: AsyncSession, booking: Booking) -> Booking:
    booking.status = BookingStatus.CANCELLED
    await db.commit()
    return await get_booking(db, booking.id)


async def change_status(db: AsyncSession, booking_id: int, new_status: BookingStatus) -> Booking:
    booking = await get_booking(db, booking_id)
    if new_status not in ADMIN_TRANSITIONS[booking.status]:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Нельзя перевести бронь из статуса «{booking.status}» в «{new_status}»",
        )
    if new_status == BookingStatus.CANCELLED:
        return await _cancel(db, booking)
    booking.status = new_status
    await db.commit()
    return await get_booking(db, booking.id)
