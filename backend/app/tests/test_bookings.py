from datetime import date, timedelta

from httpx import AsyncClient

from app.models import Car


def _payload(car: Car, start: date, days: int, **extra: str) -> dict:
    return {
        "car_id": car.id,
        "pickup_location": "Офис",
        "return_location": "Аэропорт",
        "start_date": str(start),
        "end_date": str(start + timedelta(days=days)),
        **extra,
    }


async def test_create_booking_price_is_server_side(
    client: AsyncClient, car: Car, auth_headers: dict[str, str], future: date
) -> None:
    payload = _payload(car, future, 3) | {"total_price": "1.00"}
    response = await client.post("/api/v1/bookings", headers=auth_headers, json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["total_price"] == "45000.00"
    assert data["days"] == 3
    assert data["status"] == "pending"
    assert data["payment_method"] == "cash"
    assert data["car"]["brand"] == "Toyota"


async def test_overlap_rejected(
    client: AsyncClient,
    car: Car,
    auth_headers: dict[str, str],
    other_headers: dict[str, str],
    future: date,
) -> None:
    first = await client.post(
        "/api/v1/bookings", headers=auth_headers, json=_payload(car, future, 3)
    )
    assert first.status_code == 201

    overlap = _payload(car, future + timedelta(days=2), 3)
    response = await client.post("/api/v1/bookings", headers=other_headers, json=overlap)
    assert response.status_code == 409
    assert response.json()["detail"] == "Автомобиль уже забронирован на выбранные даты"

    # Начало в день возврата — допустимо
    adjacent = _payload(car, future + timedelta(days=3), 2)
    response = await client.post("/api/v1/bookings", headers=other_headers, json=adjacent)
    assert response.status_code == 201


async def test_cancelled_booking_frees_dates(
    client: AsyncClient,
    car: Car,
    auth_headers: dict[str, str],
    other_headers: dict[str, str],
    future: date,
) -> None:
    first = await client.post(
        "/api/v1/bookings", headers=auth_headers, json=_payload(car, future, 3)
    )
    booking_id = first.json()["id"]
    cancel = await client.post(f"/api/v1/bookings/{booking_id}/cancel", headers=auth_headers)
    assert cancel.status_code == 200
    assert cancel.json()["status"] == "cancelled"

    response = await client.post(
        "/api/v1/bookings", headers=other_headers, json=_payload(car, future, 3)
    )
    assert response.status_code == 201


async def test_past_dates_rejected(
    client: AsyncClient, car: Car, auth_headers: dict[str, str], future: date
) -> None:
    past = future - timedelta(days=30)
    response = await client.post(
        "/api/v1/bookings", headers=auth_headers, json=_payload(car, past, 2)
    )
    assert response.status_code == 400
    assert "прошедшие" in response.json()["detail"]


async def test_end_before_start_rejected(
    client: AsyncClient, car: Car, auth_headers: dict[str, str], future: date
) -> None:
    payload = _payload(car, future, 0)
    response = await client.post("/api/v1/bookings", headers=auth_headers, json=payload)
    assert response.status_code == 400


async def test_my_bookings_and_isolation(
    client: AsyncClient,
    car: Car,
    auth_headers: dict[str, str],
    other_headers: dict[str, str],
    future: date,
) -> None:
    created = await client.post(
        "/api/v1/bookings", headers=auth_headers, json=_payload(car, future, 2)
    )
    booking_id = created.json()["id"]

    mine = await client.get("/api/v1/bookings/my", headers=auth_headers)
    assert [b["id"] for b in mine.json()] == [booking_id]
    assert (await client.get("/api/v1/bookings/my", headers=other_headers)).json() == []

    # Чужую бронь нельзя ни увидеть, ни отменить
    assert (
        await client.get(f"/api/v1/bookings/{booking_id}", headers=other_headers)
    ).status_code == 404
    response = await client.post(f"/api/v1/bookings/{booking_id}/cancel", headers=other_headers)
    assert response.status_code == 404


async def test_booking_requires_auth(client: AsyncClient, car: Car, future: date) -> None:
    response = await client.post("/api/v1/bookings", json=_payload(car, future, 2))
    assert response.status_code == 401
