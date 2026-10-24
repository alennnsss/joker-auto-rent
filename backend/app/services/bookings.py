from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from zoneinfo import ZoneInfo

from fastapi import HTTPException, status
from sqlalchemy import exists, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models import Booking, BookingStatus, Car, User
from app.schemas.booking import BookingCreate
from app.services.cars import overlap_clause

USER_CANCELLABLE = {BookingStatus.PENDING, BookingStatus.CONFIRMED}

# Допустимые смены статуса администратором
ADMIN_TRANSITIONS: dict[BookingStatus, set[BookingStatus]] = {
    BookingStatus.PENDING: {BookingStatus.CONFIRMED, BookingStatus.CANCELLED},
    BookingStatus.CONFIRMED: {BookingStatus.ACTIVE, BookingStatus.CANCELLED},
    BookingStatus.ACTIVE: {BookingStatus.COMPLETED},
    BookingStatus.COMPLETED: set(),
    BookingStatus.CANCELLED: set(),
}

CONFLICT_DETAIL = "Автомобиль уже забронирован на выбранные даты"


def today(settings: Settings) -> date:
    return datetime.now(ZoneInfo(settings.timezone)).date()


def calculate_price(price_per_day: Decimal, start: date, end: date) -> Decimal:
    days = (end - start).days
    return (price_per_day * days).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def validate_dates(start: date, end: date, settings: Settings) -> None:
    if end <= start:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Дата окончания должна быть позже даты начала"
        )
    if start < today(settings):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Нельзя забронировать на прошедшие даты")
    if (end - start).days > settings.max_booking_days:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Максимальный срок аренды — {settings.max_booking_days} дней",
        )


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


async def create_booking(
    db: AsyncSession,
    user: User,
    data: BookingCreate,
    settings: Settings,
) -> Booking:
    validate_dates(data.start_date, data.end_date, settings)

    if not user.email_verified:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "Подтвердите email, чтобы оформить бронирование"
        )

    # Блокируем строку авто, чтобы параллельные брони одного авто шли последовательно
    car = await db.get(Car, data.car_id, with_for_update=True)
    if car is None or not car.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Автомобиль не найден")
    if not await is_car_available(db, car.id, data.start_date, data.end_date):
        raise HTTPException(status.HTTP_409_CONFLICT, CONFLICT_DETAIL)

    booking = Booking(
        user_id=user.id,
        car_id=car.id,
        start_date=data.start_date,
        end_date=data.end_date,
        pickup_location=data.pickup_location.strip(),
        return_location=data.return_location.strip(),
        pickup_time=data.pickup_time,
        return_time=data.return_time,
        # Цена считается только на сервере
        total_price=calculate_price(car.price_per_day, data.start_date, data.end_date),
        status=BookingStatus.PENDING,
    )
    db.add(booking)
    try:
        await db.commit()
    except IntegrityError:
        # Сработал exclusion constraint в PostgreSQL
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, CONFLICT_DETAIL) from None
    return await get_booking(db, booking.id)


async def list_user_bookings(db: AsyncSession, user: User) -> list[Booking]:
    stmt = select(Booking).where(Booking.user_id == user.id).order_by(Booking.id.desc())
    return list(await db.scalars(stmt))


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


async def cancel_by_user(db: AsyncSession, booking_id: int, user: User) -> Booking:
    booking = await get_booking(db, booking_id, user)
    if booking.status not in USER_CANCELLABLE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Эту бронь уже нельзя отменить")
    return await _cancel(db, booking)


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
