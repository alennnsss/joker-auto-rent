from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.core.deps import AppSettings, DbSession
from app.schemas.car import AvailabilityOut, CarFilters, CarListOut, CarOut, CategoryOut, DateRange
from app.services import bookings as booking_service
from app.services import cars as car_service

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("", response_model=CarListOut)
async def list_cars(db: DbSession, filters: Annotated[CarFilters, Query()]) -> CarListOut:
    cars, total = await car_service.list_cars(db, filters)
    return CarListOut(items=[CarOut.model_validate(car) for car in cars], total=total)


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: DbSession) -> list[CategoryOut]:
    return [CategoryOut.model_validate(c) for c in await car_service.list_categories(db)]


@router.get("/{car_id}", response_model=CarOut)
async def get_car(car_id: int, db: DbSession) -> CarOut:
    return CarOut.model_validate(await car_service.get_car(db, car_id))


@router.get("/{car_id}/availability", response_model=AvailabilityOut)
async def get_availability(
    car_id: int,
    db: DbSession,
    settings: AppSettings,
    start_date: date | None = None,
    end_date: date | None = None,
) -> AvailabilityOut:
    car = await car_service.get_car(db, car_id)
    ranges = await car_service.busy_ranges(db, car.id, booking_service.today(settings))
    result = AvailabilityOut(
        car_id=car.id, busy=[DateRange(start_date=s, end_date=e) for s, e in ranges]
    )
    if start_date and end_date:
        if end_date <= start_date:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Дата окончания должна быть позже даты начала"
            )
        result.available = await booking_service.is_car_available(db, car.id, start_date, end_date)
        result.days = (end_date - start_date).days
        result.total_price = booking_service.calculate_price(
            car.price_per_day, start_date, end_date
        )
    return result
