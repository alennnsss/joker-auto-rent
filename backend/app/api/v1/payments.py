from fastapi import APIRouter, Request

from app.core.deps import CurrentUser, DbSession, Provider
from app.schemas.payment import PaymentCreateOut
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/{booking_id}/create", response_model=PaymentCreateOut)
async def create_payment(
    booking_id: int, user: CurrentUser, db: DbSession, provider: Provider
) -> PaymentCreateOut:
    return await payment_service.create_online_payment(db, booking_id, user, provider)


@router.post("/webhook")
async def payment_webhook(request: Request, db: DbSession, provider: Provider) -> dict[str, str]:
    body = await request.body()
    await payment_service.handle_webhook(db, provider, dict(request.headers), body)
    return {"status": "ok"}
