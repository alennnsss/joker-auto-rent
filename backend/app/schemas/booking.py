from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models import BookingStatus
from app.schemas.auth import UserOut
from app.schemas.car import CarShort


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    car: CarShort
    start_date: date
    end_date: date
    pickup_location: str
    return_location: str
    pickup_time: time
    return_time: time
    days: int
    total_price: Decimal
    status: BookingStatus
    created_at: datetime


class AdminBookingOut(BookingOut):
    user: UserOut


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
