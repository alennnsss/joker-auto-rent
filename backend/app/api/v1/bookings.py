from fastapi import APIRouter, status

from app.core.deps import AppSettings, CurrentUser, DbSession, Provider
from app.schemas.booking import BookingCreate, BookingOut
from app.services import bookings as booking_service

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: BookingCreate,
    user: CurrentUser,
    db: DbSession,
    provider: Provider,
    settings: AppSettings,
) -> BookingOut:
    booking = await booking_service.create_booking(db, user, data, provider, settings)
    return BookingOut.model_validate(booking)


@router.get("/my", response_model=list[BookingOut])
async def my_bookings(user: CurrentUser, db: DbSession) -> list[BookingOut]:
    bookings = await booking_service.list_user_bookings(db, user)
    return [BookingOut.model_validate(b) for b in bookings]


@router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(booking_id: int, user: CurrentUser, db: DbSession) -> BookingOut:
    return BookingOut.model_validate(await booking_service.get_booking(db, booking_id, user))


@router.post("/{booking_id}/cancel", response_model=BookingOut)
async def cancel_booking(
    booking_id: int, user: CurrentUser, db: DbSession, provider: Provider
) -> BookingOut:
    booking = await booking_service.cancel_by_user(db, booking_id, user, provider)
    return BookingOut.model_validate(booking)
