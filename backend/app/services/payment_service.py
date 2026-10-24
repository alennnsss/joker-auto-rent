from collections.abc import Mapping

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Booking, BookingStatus, Payment, PaymentMethod, PaymentStatus, User
from app.schemas.payment import PaymentCreateOut
from app.services.bookings import get_booking
from app.services.payments import PaymentProvider, PaymentProviderError

# Из финальных статусов платёж не откатывается (защита от поздних/повторных webhook)
ALLOWED_PAYMENT_TRANSITIONS: dict[PaymentStatus, set[PaymentStatus]] = {
    PaymentStatus.PENDING: {PaymentStatus.SUCCEEDED, PaymentStatus.FAILED},
    PaymentStatus.FAILED: {PaymentStatus.SUCCEEDED},
    PaymentStatus.SUCCEEDED: {PaymentStatus.REFUNDED},
    PaymentStatus.REFUNDED: set(),
}


def apply_payment_status(booking: Booking, payment: Payment, new_status: PaymentStatus) -> None:
    payment.status = new_status
    if new_status == PaymentStatus.SUCCEEDED and booking.status == BookingStatus.PENDING:
        booking.status = BookingStatus.CONFIRMED


async def create_online_payment(
    db: AsyncSession, booking_id: int, user: User, provider: PaymentProvider
) -> PaymentCreateOut:
    booking = await get_booking(db, booking_id, user)
    if booking.payment_method != PaymentMethod.ONLINE:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Для этой брони выбрана оплата при получении"
        )
    if booking.is_paid:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Бронь уже оплачена")
    if booking.status != BookingStatus.PENDING:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Эту бронь нельзя оплатить")
    if not provider.supports_online:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Онлайн-оплата пока недоступна")

    try:
        init = await provider.create_payment(booking, booking.total_price)
    except PaymentProviderError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc

    payment = Payment(
        booking_id=booking.id,
        amount=booking.total_price,
        provider=provider.name,
        provider_payment_id=init.provider_payment_id,
        status=PaymentStatus.PENDING,
    )
    db.add(payment)
    if init.status != PaymentStatus.PENDING:
        apply_payment_status(booking, payment, init.status)
    await db.commit()
    return PaymentCreateOut(
        payment_id=payment.id, status=payment.status, redirect_url=init.redirect_url
    )


async def handle_webhook(
    db: AsyncSession, provider: PaymentProvider, headers: Mapping[str, str], body: bytes
) -> None:
    if not provider.verify_webhook(headers, body):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Неверная подпись запроса")
    try:
        event = provider.parse_webhook(body)
    except ValueError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Некорректное тело запроса") from None

    payment = await db.scalar(
        select(Payment)
        .where(
            Payment.provider == provider.name,
            Payment.provider_payment_id == event.provider_payment_id,
        )
        .with_for_update()
    )
    if payment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Платёж не найден")

    # Идемпотентность: повтор того же события или недопустимый переход ничего не меняют
    if event.status not in ALLOWED_PAYMENT_TRANSITIONS[payment.status]:
        return
    booking = await get_booking(db, payment.booking_id)
    apply_payment_status(booking, payment, event.status)
    await db.commit()


async def list_payments(db: AsyncSession, limit: int, offset: int) -> list[Payment]:
    stmt = select(Payment).order_by(Payment.id.desc()).limit(limit).offset(offset)
    return list(await db.scalars(stmt))
