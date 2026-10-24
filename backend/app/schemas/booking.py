from datetime import date, datetime, time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models import BookingStatus, PaymentMethod
from app.schemas.auth import UserOut
from app.schemas.car import CarShort


class BookingCreate(BaseModel):
    car_id: int
    start_date: date
    end_date: date
    pickup_location: str = Field(min_length=2, max_length=255)
    return_location: str = Field(min_length=2, max_length=255)
    pickup_time: time = time(10, 0)
    return_time: time = time(10, 0)
    payment_method: PaymentMethod = PaymentMethod.CASH


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
    payment_method: PaymentMethod
    status: BookingStatus
    is_paid: bool
    created_at: datetime


class AdminBookingOut(BookingOut):
    user: UserOut


class BookingStatusUpdate(BaseModel):
    status: BookingStatus
