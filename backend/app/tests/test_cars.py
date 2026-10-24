from datetime import date, timedelta

from httpx import AsyncClient

from app.models import Car


async def test_list_cars(client: AsyncClient, car: Car) -> None:
    response = await client.get("/api/v1/cars")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["brand"] == "Toyota"
    assert data["items"][0]["category"]["name"] == "Комфорт"
    assert data["items"][0]["price_per_day"] == "15000.00"


async def test_filters(client: AsyncClient, car: Car) -> None:
    params = {"min_price": 20000}
    assert (await client.get("/api/v1/cars", params=params)).json()["total"] == 0
    params = {"max_price": 20000, "seats": 5, "transmission": "automatic"}
    assert (await client.get("/api/v1/cars", params=params)).json()["total"] == 1
    params = {"transmission": "manual"}
    assert (await client.get("/api/v1/cars", params=params)).json()["total"] == 0


async def test_filter_requires_both_dates(client: AsyncClient, car: Car) -> None:
    response = await client.get("/api/v1/cars", params={"start_date": "2030-01-01"})
    assert response.status_code == 422
    assert "обе даты" in response.json()["detail"]


async def test_availability_filter_excludes_booked(
    client: AsyncClient, car: Car, make_booking, future: date
) -> None:
    end = future + timedelta(days=3)
    await make_booking(car, future, 3)
    params = {"start_date": str(future + timedelta(days=1)), "end_date": str(end)}
    assert (await client.get("/api/v1/cars", params=params)).json()["total"] == 0
    # День возврата свободен
    params = {"start_date": str(end), "end_date": str(end + timedelta(days=2))}
    assert (await client.get("/api/v1/cars", params=params)).json()["total"] == 1


async def test_get_car_not_found(client: AsyncClient) -> None:
    response = await client.get("/api/v1/cars/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Автомобиль не найден"


async def test_availability_quote(client: AsyncClient, car: Car, future: date) -> None:
    response = await client.get(
        f"/api/v1/cars/{car.id}/availability",
        params={"start_date": str(future), "end_date": str(future + timedelta(days=3))},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["available"] is True
    assert data["days"] == 3
    assert data["total_price"] == "45000.00"


async def test_categories(client: AsyncClient, car: Car) -> None:
    response = await client.get("/api/v1/cars/categories")
    assert response.status_code == 200
    assert [c["name"] for c in response.json()] == ["Комфорт"]
