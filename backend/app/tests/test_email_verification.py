from datetime import date, timedelta

from httpx import AsyncClient

from app.models import Car
from app.tests.conftest import last_code, register_user


async def test_register_sends_code_and_user_is_unverified(
    client: AsyncClient, outbox: list[dict[str, str]]
) -> None:
    headers = await register_user(client, outbox, "new@example.com", verify=False)
    assert outbox[-1]["to"] == "new@example.com"
    assert len(last_code(outbox, "new@example.com")) == 6

    me = (await client.get("/api/v1/auth/me", headers=headers)).json()
    assert me["email_verified"] is False


async def test_verify_with_correct_code(client: AsyncClient, outbox: list[dict[str, str]]) -> None:
    headers = await register_user(client, outbox, "new@example.com", verify=False)
    code = last_code(outbox, "new@example.com")

    response = await client.post("/api/v1/auth/verify-email", headers=headers, json={"code": code})
    assert response.status_code == 200
    assert response.json()["email_verified"] is True


async def test_wrong_code_and_attempt_limit(
    client: AsyncClient, outbox: list[dict[str, str]]
) -> None:
    headers = await register_user(client, outbox, "new@example.com", verify=False)
    code = last_code(outbox, "new@example.com")
    wrong = "000000" if code != "000000" else "111111"

    for _ in range(5):
        response = await client.post(
            "/api/v1/auth/verify-email", headers=headers, json={"code": wrong}
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Неверный код"

    # После 5 ошибок даже верный код не принимается — нужен новый
    response = await client.post("/api/v1/auth/verify-email", headers=headers, json={"code": code})
    assert response.status_code == 429


async def test_resend_has_cooldown(client: AsyncClient, outbox: list[dict[str, str]]) -> None:
    headers = await register_user(client, outbox, "new@example.com", verify=False)
    response = await client.post("/api/v1/auth/resend-verification", headers=headers)
    assert response.status_code == 429
    assert "через" in response.json()["detail"]


async def test_resend_for_verified_user(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post("/api/v1/auth/resend-verification", headers=auth_headers)
    assert response.status_code == 400


async def test_booking_requires_verified_email(
    client: AsyncClient, outbox: list[dict[str, str]], car: Car, future: date
) -> None:
    headers = await register_user(client, outbox, "new@example.com", verify=False)
    response = await client.post(
        "/api/v1/bookings",
        headers=headers,
        json={
            "car_id": car.id,
            "pickup_location": "Офис",
            "return_location": "Офис",
            "start_date": str(future),
            "end_date": str(future + timedelta(days=2)),
        },
    )
    assert response.status_code == 403
    assert "Подтвердите email" in response.json()["detail"]


async def test_booking_stores_locations_and_times(
    client: AsyncClient, auth_headers: dict[str, str], car: Car, future: date
) -> None:
    response = await client.post(
        "/api/v1/bookings",
        headers=auth_headers,
        json={
            "car_id": car.id,
            "pickup_location": "Аэропорт Алматы",
            "return_location": "Офис",
            "pickup_time": "08:30",
            "return_time": "20:00",
            "start_date": str(future),
            "end_date": str(future + timedelta(days=2)),
        },
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["pickup_location"] == "Аэропорт Алматы"
    assert data["return_location"] == "Офис"
    assert data["pickup_time"] == "08:30:00"
    assert data["return_time"] == "20:00:00"
