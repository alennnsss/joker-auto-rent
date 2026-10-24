import os
import re
from collections.abc import AsyncIterator
from datetime import date, timedelta
from decimal import Decimal

# Тесты по умолчанию идут на SQLite; для проверки на PostgreSQL задайте TEST_DATABASE_URL
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ["ENV"] = "development"
os.environ["PAYMENT_PROVIDER"] = "mock"
os.environ["JWT_SECRET"] = "test-secret-key-with-at-least-32-bytes"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Car, CarCategory, Fuel, Transmission, User, UserRole
from app.services import email as email_service
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


async def register_user(
    client: AsyncClient, outbox: list[dict[str, str]], email: str, *, verify: bool = True
) -> dict[str, str]:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "Тест Тестов",
            "phone": "87011234567",
        },
    )
    assert response.status_code == 201, response.text
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}
    if verify:
        code = last_code(outbox, email)
        verified = await client.post(
            "/api/v1/auth/verify-email", headers=headers, json={"code": code}
        )
        assert verified.status_code == 200, verified.text
    return headers


def last_code(outbox: list[dict[str, str]], email: str) -> str:
    """Код подтверждения из последнего письма на адрес email."""
    body = next(m["body"] for m in reversed(outbox) if m["to"] == email)
    match = re.search(r"\b(\d{6})\b", body)
    assert match, body
    return match.group(1)


@pytest.fixture(autouse=True)
def outbox(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, str]]:
    """Перехватывает письма вместо отправки по SMTP."""
    sent: list[dict[str, str]] = []

    async def fake_send(settings, to: str, subject: str, body: str) -> None:
        sent.append({"to": to, "subject": subject, "body": body})

    monkeypatch.setattr(email_service, "send_email", fake_send)
    return sent


@pytest.fixture
async def auth_headers(client: AsyncClient, outbox: list[dict[str, str]]) -> dict[str, str]:
    return await register_user(client, outbox, "client@example.com")


@pytest.fixture
async def other_headers(client: AsyncClient, outbox: list[dict[str, str]]) -> dict[str, str]:
    return await register_user(client, outbox, "other@example.com")


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
    response = await client.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": "adminpass1"}
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def future() -> date:
    """Дата через неделю в часовом поясе Алматы."""
    return today(get_settings()) + timedelta(days=7)
