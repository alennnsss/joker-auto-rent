"""Начальные данные: категории, администратор, демо-автомобили.

Запуск: python -m app.seed  (повторный запуск безопасен)
"""

import asyncio
import os
from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Car, CarCategory, CarImage, Fuel, Transmission, User, UserRole

CATEGORIES = ["Эконом", "Комфорт", "Бизнес", "SUV", "Минивэн"]

UNSPLASH = "https://images.unsplash.com/{}?auto=format&fit=crop&w=1200&q=80"

DEMO_CARS = [
    (
        "Hyundai",
        "Accent",
        2022,
        "Эконом",
        Transmission.AUTOMATIC,
        Fuel.PETROL,
        5,
        15000,
        50000,
        "photo-1549317661-bd32c8ce0db2",
    ),
    (
        "Kia",
        "Rio",
        2023,
        "Эконом",
        Transmission.AUTOMATIC,
        Fuel.PETROL,
        5,
        16000,
        50000,
        "photo-1552519507-da3b142c6e3d",
    ),
    (
        "Toyota",
        "Camry 70",
        2023,
        "Комфорт",
        Transmission.AUTOMATIC,
        Fuel.PETROL,
        5,
        30000,
        100000,
        "photo-1621007947382-bb3c3994e3fb",
    ),
    (
        "Hyundai",
        "Sonata",
        2022,
        "Комфорт",
        Transmission.AUTOMATIC,
        Fuel.PETROL,
        5,
        28000,
        100000,
        "photo-1494976388531-d1058494cdd8",
    ),
    (
        "Mercedes-Benz",
        "E-Class",
        2022,
        "Бизнес",
        Transmission.AUTOMATIC,
        Fuel.PETROL,
        5,
        60000,
        200000,
        "photo-1618843479313-40f8afb4b4d8",
    ),
    (
        "BMW",
        "5 Series",
        2023,
        "Бизнес",
        Transmission.AUTOMATIC,
        Fuel.DIESEL,
        5,
        65000,
        200000,
        "photo-1555215695-3004980ad54e",
    ),
    (
        "Toyota",
        "Land Cruiser 300",
        2023,
        "SUV",
        Transmission.AUTOMATIC,
        Fuel.DIESEL,
        7,
        90000,
        300000,
        "photo-1519641471654-76ce0107ad1b",
    ),
    (
        "Lexus",
        "LX 600",
        2023,
        "SUV",
        Transmission.AUTOMATIC,
        Fuel.PETROL,
        7,
        120000,
        400000,
        "photo-1533473359331-0135ef1b58bf",
    ),
    (
        "Hyundai",
        "Staria",
        2023,
        "Минивэн",
        Transmission.AUTOMATIC,
        Fuel.DIESEL,
        9,
        45000,
        150000,
        "photo-1559416523-140ddc3d238c",
    ),
]


async def seed() -> None:
    async with SessionLocal() as db:
        categories: dict[str, CarCategory] = {
            c.name: c for c in await db.scalars(select(CarCategory))
        }
        for name in CATEGORIES:
            if name not in categories:
                categories[name] = CarCategory(name=name)
                db.add(categories[name])

        admin_email = os.getenv("ADMIN_EMAIL", "admin@joker.kz")
        if not await db.scalar(select(User).where(User.email == admin_email)):
            db.add(
                User(
                    email=admin_email,
                    full_name="Администратор",
                    phone=None,
                    password_hash=hash_password(os.getenv("ADMIN_PASSWORD", "admin12345")),
                    role=UserRole.ADMIN,
                    email_verified=True,
                )
            )

        if not await db.scalar(select(Car.id).limit(1)):
            for brand, model, year, cat, trans, fuel, seats, price, deposit, photo in DEMO_CARS:
                car = Car(
                    brand=brand,
                    model=model,
                    year=year,
                    category=categories[cat],
                    transmission=trans,
                    fuel=fuel,
                    seats=seats,
                    price_per_day=Decimal(price),
                    deposit=Decimal(deposit),
                    description=f"{brand} {model} {year} года в отличном состоянии. "
                    "Полная страховка, чистый салон, подача по Алматы.",
                )
                car.images = [CarImage(url=UNSPLASH.format(photo), sort_order=0)]
                db.add(car)

        await db.commit()
    print("Seed completed")


if __name__ == "__main__":
    asyncio.run(seed())
