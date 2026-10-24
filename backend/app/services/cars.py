from datetime import date
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models import BLOCKING_STATUSES, Booking, Car, CarCategory, CarImage
from app.schemas.car import CarCreate, CarFilters, CarUpdate

ALLOWED_IMAGE_TYPES = {"image/webp": "webp", "image/jpeg": "jpg", "image/png": "png"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024


def overlap_clause(start: date, end: date):
    """Брони, пересекающиеся с [start, end) и блокирующие авто."""
    return (
        Booking.status.in_(BLOCKING_STATUSES),
        Booking.start_date < end,
        Booking.end_date > start,
    )


async def list_categories(db: AsyncSession) -> list[CarCategory]:
    return list(await db.scalars(select(CarCategory).order_by(CarCategory.id)))


async def create_category(db: AsyncSession, name: str) -> CarCategory:
    if await db.scalar(select(CarCategory).where(func.lower(CarCategory.name) == name.lower())):
        raise HTTPException(status.HTTP_409_CONFLICT, "Такая категория уже существует")
    category = CarCategory(name=name.strip())
    db.add(category)
    await db.commit()
    return category


async def list_cars(
    db: AsyncSession, filters: CarFilters, *, include_inactive: bool = False
) -> tuple[list[Car], int]:
    stmt = select(Car)
    if not include_inactive:
        stmt = stmt.where(Car.is_active.is_(True))
    if filters.category_id is not None:
        stmt = stmt.where(Car.category_id == filters.category_id)
    if filters.transmission is not None:
        stmt = stmt.where(Car.transmission == filters.transmission)
    if filters.min_price is not None:
        stmt = stmt.where(Car.price_per_day >= filters.min_price)
    if filters.max_price is not None:
        stmt = stmt.where(Car.price_per_day <= filters.max_price)
    if filters.seats is not None:
        stmt = stmt.where(Car.seats >= filters.seats)
    if filters.start_date and filters.end_date:
        busy = exists().where(
            Booking.car_id == Car.id, *overlap_clause(filters.start_date, filters.end_date)
        )
        stmt = stmt.where(~busy)

    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0

    order = {
        "price_asc": (Car.price_per_day.asc(), Car.id),
        "price_desc": (Car.price_per_day.desc(), Car.id),
        "newest": (Car.created_at.desc(), Car.id.desc()),
    }[filters.sort]
    stmt = stmt.order_by(*order).limit(filters.limit).offset(filters.offset)
    return list(await db.scalars(stmt)), total


async def get_car(db: AsyncSession, car_id: int, *, include_inactive: bool = False) -> Car:
    car = await db.get(Car, car_id)
    if car is None or (not car.is_active and not include_inactive):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Автомобиль не найден")
    return car


async def busy_ranges(db: AsyncSession, car_id: int, from_date: date) -> list[tuple[date, date]]:
    rows = await db.execute(
        select(Booking.start_date, Booking.end_date)
        .where(
            Booking.car_id == car_id,
            Booking.status.in_(BLOCKING_STATUSES),
            Booking.end_date > from_date,
        )
        .order_by(Booking.start_date)
    )
    return [(row.start_date, row.end_date) for row in rows]


async def _ensure_category(db: AsyncSession, category_id: int) -> None:
    if await db.get(CarCategory, category_id) is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Категория не найдена")


async def _reload(db: AsyncSession, car_id: int) -> Car:
    car = await db.scalar(
        select(Car).where(Car.id == car_id).execution_options(populate_existing=True)
    )
    assert car is not None
    return car


async def create_car(db: AsyncSession, data: CarCreate) -> Car:
    await _ensure_category(db, data.category_id)
    car = Car(**data.model_dump())
    db.add(car)
    await db.commit()
    return await _reload(db, car.id)


async def update_car(db: AsyncSession, car_id: int, data: CarUpdate) -> Car:
    car = await get_car(db, car_id, include_inactive=True)
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    if "category_id" in changes:
        await _ensure_category(db, changes["category_id"])
    for field, value in changes.items():
        setattr(car, field, value)
    await db.commit()
    return await _reload(db, car.id)


async def delete_car(db: AsyncSession, car_id: int, settings: Settings) -> None:
    car = await get_car(db, car_id, include_inactive=True)
    if await db.scalar(select(exists().where(Booking.car_id == car_id))):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "У автомобиля есть бронирования — удалить нельзя, сделайте его неактивным",
        )
    image_urls = [image.url for image in car.images]
    await db.delete(car)
    await db.commit()
    for url in image_urls:
        _remove_local_file(url, settings)


async def add_image(db: AsyncSession, car_id: int, file: UploadFile, settings: Settings) -> Car:
    car = await get_car(db, car_id, include_inactive=True)
    ext = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if ext is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Допустимые форматы: WebP, JPEG, PNG")
    content = await file.read(MAX_IMAGE_SIZE + 1)
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Файл больше 10 МБ")

    target_dir = Path(settings.media_dir) / "cars"
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}.{ext}"
    (target_dir / filename).write_bytes(content)

    next_order = max((image.sort_order for image in car.images), default=-1) + 1
    db.add(CarImage(car_id=car.id, url=f"/media/cars/{filename}", sort_order=next_order))
    await db.commit()
    return await _reload(db, car.id)


async def add_image_url(db: AsyncSession, car_id: int, url: str) -> Car:
    car = await get_car(db, car_id, include_inactive=True)
    next_order = max((image.sort_order for image in car.images), default=-1) + 1
    db.add(CarImage(car_id=car.id, url=url, sort_order=next_order))
    await db.commit()
    return await _reload(db, car.id)


async def delete_image(db: AsyncSession, car_id: int, image_id: int, settings: Settings) -> Car:
    image = await db.get(CarImage, image_id)
    if image is None or image.car_id != car_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Фото не найдено")
    url = image.url
    await db.delete(image)
    await db.commit()
    _remove_local_file(url, settings)
    return await _reload(db, car_id)


def _remove_local_file(url: str, settings: Settings) -> None:
    if url.startswith("/media/"):
        path = Path(settings.media_dir) / url.removeprefix("/media/")
        path.unlink(missing_ok=True)
