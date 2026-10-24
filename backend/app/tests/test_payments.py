from datetime import date, timedelta

import pytest
from httpx import AsyncClient

from app.core.config import Settings
from app.models import Car
from app.services.payments import build_payment_provider
from app.services.payments.cash import CashPaymentProvider
from app.services.payments.mock import MockPaymentProvider


async def _online_booking(client: AsyncClient, car: Car, headers: dict, start: date) -> int:
    response = await client.post(
        "/api/v1/bookings",
        headers=headers,
        json={
            "car_id": car.id,
            "pickup_location": "Офис",
            "return_location": "Аэропорт",
            "start_date": str(start),
            "end_date": str(start + timedelta(days=2)),
            "payment_method": "online",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def test_public_config(client: AsyncClient) -> None:
    response = await client.get("/api/v1/config")
    assert response.json() == {
        "currency": "KZT",
        "timezone": "Asia/Almaty",
        "online_payment_enabled": True,
    }


async def test_mock_payment_confirms_booking(
    client: AsyncClient, car: Car, auth_headers: dict[str, str], future: date
) -> None:
    booking_id = await _online_booking(client, car, auth_headers, future)

    response = await client.post(f"/api/v1/payments/{booking_id}/create", headers=auth_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "succeeded"
    assert data["redirect_url"].endswith(f"/payment/success?booking={booking_id}")

    booking = (await client.get(f"/api/v1/bookings/{booking_id}", headers=auth_headers)).json()
    assert booking["status"] == "confirmed"
    assert booking["is_paid"] is True

    # Повторная оплата запрещена
    again = await client.post(f"/api/v1/payments/{booking_id}/create", headers=auth_headers)
    assert again.status_code == 400


async def test_cash_booking_cannot_be_paid_online(
    client: AsyncClient, car: Car, auth_headers: dict[str, str], future: date
) -> None:
    created = await client.post(
        "/api/v1/bookings",
        headers=auth_headers,
        json={
            "car_id": car.id,
            "pickup_location": "Офис",
            "return_location": "Аэропорт",
            "start_date": str(future),
            "end_date": str(future + timedelta(days=1)),
        },
    )
    booking_id = created.json()["id"]
    response = await client.post(f"/api/v1/payments/{booking_id}/create", headers=auth_headers)
    assert response.status_code == 400


async def test_webhook_is_idempotent_and_refund_on_cancel(
    client: AsyncClient,
    car: Car,
    auth_headers: dict[str, str],
    admin_headers: dict[str, str],
    future: date,
) -> None:
    booking_id = await _online_booking(client, car, auth_headers, future)
    await client.post(f"/api/v1/payments/{booking_id}/create", headers=auth_headers)
    payment = (await client.get("/api/v1/admin/payments", headers=admin_headers)).json()[0]

    # Повторный webhook с тем же статусом и поздний "failed" ничего не меняют
    for status in ("succeeded", "succeeded", "failed"):
        response = await client.post(
            "/api/v1/payments/webhook",
            json={"payment_id": payment["provider_payment_id"], "status": status},
        )
        assert response.status_code == 200
    payment = (await client.get("/api/v1/admin/payments", headers=admin_headers)).json()[0]
    assert payment["status"] == "succeeded"

    await client.post(f"/api/v1/bookings/{booking_id}/cancel", headers=auth_headers)
    payment = (await client.get("/api/v1/admin/payments", headers=admin_headers)).json()[0]
    assert payment["status"] == "refunded"


async def test_webhook_unknown_payment(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/payments/webhook", json={"payment_id": "mock_nope", "status": "succeeded"}
    )
    assert response.status_code == 404


async def test_webhook_bad_body(client: AsyncClient) -> None:
    response = await client.post("/api/v1/payments/webhook", content=b"not json")
    assert response.status_code == 400


def test_mock_forbidden_in_production() -> None:
    settings = Settings(env="production", jwt_secret="prod-secret", payment_provider="mock")
    with pytest.raises(RuntimeError):
        build_payment_provider(settings)


def test_factory_selects_provider() -> None:
    assert isinstance(
        build_payment_provider(Settings(payment_provider="mock")), MockPaymentProvider
    )
    cash = build_payment_provider(Settings(payment_provider="cash"))
    assert isinstance(cash, CashPaymentProvider)
    assert cash.supports_online is False
    with pytest.raises(RuntimeError):
        build_payment_provider(Settings(payment_provider="unknown"))
