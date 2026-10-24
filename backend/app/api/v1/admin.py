from typing import Annotated

from fastapi import APIRouter, Depends, Query, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.deps import AppSettings, DbSession, Provider, require_admin
from app.models import BookingStatus, User
from app.schemas.auth import UserOut
from app.schemas.booking import AdminBookingOut, BookingStatusUpdate
from app.schemas.car import (
    CarCreate,
    CarFilters,
    CarListOut,
    CarOut,
    CarUpdate,
    CategoryIn,
    CategoryOut,
)
from app.schemas.payment import PaymentOut
from app.services import bookings as booking_service
from app.services import cars as car_service
from app.services import payment_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])

Limit = Annotated[int, Query(ge=1, le=200)]
Offset = Annotated[int, Query(ge=0)]


class ImageUrlIn(BaseModel):
    url: str = Field(min_length=1, max_length=512, pattern=r"^(https://|/media/)")


# --- Автомобили ---


@router.get("/cars", response_model=CarListOut)
async def list_cars(db: DbSession, filters: Annotated[CarFilters, Query()]) -> CarListOut:
    cars, total = await car_service.list_cars(db, filters, include_inactive=True)
    return CarListOut(items=[CarOut.model_validate(car) for car in cars], total=total)


@router.get("/cars/{car_id}", response_model=CarOut)
async def get_car(car_id: int, db: DbSession) -> CarOut:
    return CarOut.model_validate(await car_service.get_car(db, car_id, include_inactive=True))


@router.post("/cars", response_model=CarOut, status_code=status.HTTP_201_CREATED)
async def create_car(data: CarCreate, db: DbSession) -> CarOut:
    return CarOut.model_validate(await car_service.create_car(db, data))


@router.patch("/cars/{car_id}", response_model=CarOut)
async def update_car(car_id: int, data: CarUpdate, db: DbSession) -> CarOut:
    return CarOut.model_validate(await car_service.update_car(db, car_id, data))


@router.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: int, db: DbSession, settings: AppSettings) -> None:
    await car_service.delete_car(db, car_id, settings)


@router.post("/cars/{car_id}/images", response_model=CarOut)
async def upload_image(
    car_id: int, file: UploadFile, db: DbSession, settings: AppSettings
) -> CarOut:
    return CarOut.model_validate(await car_service.add_image(db, car_id, file, settings))


@router.post("/cars/{car_id}/images/url", response_model=CarOut)
async def add_image_url(car_id: int, data: ImageUrlIn, db: DbSession) -> CarOut:
    return CarOut.model_validate(await car_service.add_image_url(db, car_id, data.url))


@router.delete("/cars/{car_id}/images/{image_id}", response_model=CarOut)
async def delete_image(car_id: int, image_id: int, db: DbSession, settings: AppSettings) -> CarOut:
    return CarOut.model_validate(await car_service.delete_image(db, car_id, image_id, settings))


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(data: CategoryIn, db: DbSession) -> CategoryOut:
    return CategoryOut.model_validate(await car_service.create_category(db, data.name))


# --- Бронирования ---


@router.get("/bookings", response_model=list[AdminBookingOut])
async def list_bookings(
    db: DbSession,
    status_filter: Annotated[BookingStatus | None, Query(alias="status")] = None,
    limit: Limit = 50,
    offset: Offset = 0,
) -> list[AdminBookingOut]:
    bookings = await booking_service.list_all_bookings(db, status_filter, limit, offset)
    return [AdminBookingOut.model_validate(b) for b in bookings]


@router.patch("/bookings/{booking_id}/status", response_model=AdminBookingOut)
async def change_booking_status(
    booking_id: int, data: BookingStatusUpdate, db: DbSession, provider: Provider
) -> AdminBookingOut:
    booking = await booking_service.change_status(db, booking_id, data.status, provider)
    return AdminBookingOut.model_validate(booking)


# --- Клиенты и платежи ---


@router.get("/users", response_model=list[UserOut])
async def list_users(db: DbSession, limit: Limit = 50, offset: Offset = 0) -> list[UserOut]:
    users = await db.scalars(select(User).order_by(User.id.desc()).limit(limit).offset(offset))
    return [UserOut.model_validate(u) for u in users]


@router.get("/payments", response_model=list[PaymentOut])
async def list_payments(db: DbSession, limit: Limit = 50, offset: Offset = 0) -> list[PaymentOut]:
    payments = await payment_service.list_payments(db, limit, offset)
    return [PaymentOut.model_validate(p) for p in payments]
