from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models import Fuel, Transmission


class CategoryIn(BaseModel):
    name: str = Field(min_length=2, max_length=64)


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CarImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    sort_order: int


class CarShort(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand: str
    model: str
    year: int
    images: list[CarImageOut]


class CarOut(CarShort):
    category: CategoryOut
    transmission: Transmission
    fuel: Fuel
    seats: int
    price_per_day: Decimal
    deposit: Decimal
    description: str
    is_active: bool
    created_at: datetime


class CarListOut(BaseModel):
    items: list[CarOut]
    total: int


class CarCreate(BaseModel):
    brand: str = Field(min_length=1, max_length=64)
    model: str = Field(min_length=1, max_length=64)
    year: int = Field(ge=1990, le=2100)
    category_id: int
    transmission: Transmission
    fuel: Fuel
    seats: int = Field(ge=1, le=60)
    price_per_day: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    deposit: Decimal = Field(default=Decimal("0"), ge=0, max_digits=10, decimal_places=2)
    description: str = ""
    is_active: bool = True


class CarUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=64)
    model: str | None = Field(default=None, min_length=1, max_length=64)
    year: int | None = Field(default=None, ge=1990, le=2100)
    category_id: int | None = None
    transmission: Transmission | None = None
    fuel: Fuel | None = None
    seats: int | None = Field(default=None, ge=1, le=60)
    price_per_day: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    deposit: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    description: str | None = None
    is_active: bool | None = None


class DateRange(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def _check_order(self) -> "DateRange":
        if self.end_date <= self.start_date:
            raise ValueError("Дата окончания должна быть позже даты начала")
        return self


class CarFilters(BaseModel):
    category_id: int | None = None
    transmission: Transmission | None = None
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
    seats: int | None = Field(default=None, ge=1, description="Минимальное количество мест")
    start_date: date | None = None
    end_date: date | None = None
    sort: Literal["price_asc", "price_desc", "newest"] = "price_asc"
    limit: int = Field(default=24, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def _check_dates(self) -> "CarFilters":
        if (self.start_date is None) != (self.end_date is None):
            raise ValueError("Укажите обе даты: начала и окончания аренды")
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValueError("Дата окончания должна быть позже даты начала")
        return self


class AvailabilityOut(BaseModel):
    car_id: int
    busy: list[DateRange]
    # Заполняются, если в запросе переданы даты
    available: bool | None = None
    days: int | None = None
    total_price: Decimal | None = None
