import os
from collections.abc import AsyncIterator
from datetime import date, time, timedelta
from decimal import Decimal

# Тесты по умолчанию идут на SQLite; для проверки на PostgreSQL задайте TEST_DATABASE_URL
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ["ENV"] = "development"
os.environ["JWT_SECRET"] = "test-secret-key-with-at-least-32-bytes"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Booking, Car, CarCategory, Fuel, Transmission, User, UserRole
from app.services.bookings import today


@pytest.fixture
async def session_factory(tmp_path) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    url = os.environ["DATABASE_URL"]
    if url.startswith("sqlite"):
        url = f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield async_sessionmaker(engine, expire_on_commit=False)
    await engine.dispose()


@pytest.fixture
async def db(session_factory) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session


@pytest.fixture
async def client(session_factory) -> AsyncIterator[AsyncClient]:
    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def car(db: AsyncSession) -> Car:
    category = CarCategory(name="Комфорт")
    car = Car(
        brand="Toyota",
        model="Camry",
        year=2023,
        category=category,
        transmission=Transmission.AUTOMATIC,
        fuel=Fuel.PETROL,
        seats=5,
        price_per_day=Decimal("15000.00"),
        deposit=Decimal("50000.00"),
        description="",
    )
    db.add(car)
    await db.commit()
    return car


async def login_headers(client: AsyncClient, email: str, password: str) -> dict[str, str]:
    response = await client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
async def client_user(db: AsyncSession) -> User:
    """Пользователь без прав администратора (например, созданный до отказа от аккаунтов)."""
    user = User(
        email="client@example.com",
        full_name="Тест Тестов",
        phone="+7 (701) 123-45-67",
        password_hash=hash_password("password123"),
        email_verified=True,
    )
    db.add(user)
    await db.commit()
    return user


@pytest.fixture
async def auth_headers(client: AsyncClient, client_user: User) -> dict[str, str]:
    return await login_headers(client, "client@example.com", "password123")


@pytest.fixture
async def admin_headers(client: AsyncClient, db: AsyncSession) -> dict[str, str]:
    db.add(
        User(
            email="admin@example.com",
            full_name="Админ",
            phone=None,
            password_hash=hash_password("adminpass1"),
            role=UserRole.ADMIN,
            email_verified=True,
        )
    )
    await db.commit()
    return await login_headers(client, "admin@example.com", "adminpass1")


@pytest.fixture
def future() -> date:
    """Дата через неделю в часовом поясе Алматы."""
    return today(get_settings()) + timedelta(days=7)


@pytest.fixture
def make_booking(db: AsyncSession, client_user: User):
    """Создаёт бронь напрямую в БД: клиентского API бронирования больше нет."""

    async def _make(car: Car, start: date, days: int) -> Booking:
        booking = Booking(
            user_id=client_user.id,
            car_id=car.id,
            start_date=start,
            end_date=start + timedelta(days=days),
            pickup_location="Офис",
            return_location="Аэропорт",
            pickup_time=time(10, 0),
            return_time=time(10, 0),
            total_price=car.price_per_day * days,
        )
        db.add(booking)
        await db.commit()
        return booking

    return _make
