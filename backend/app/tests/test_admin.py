from datetime import date

from httpx import AsyncClient

from app.models import Car


async def test_admin_requires_role(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get("/api/v1/admin/cars", headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Недостаточно прав"


async def test_car_crud(client: AsyncClient, car: Car, admin_headers: dict[str, str]) -> None:
    payload = {
        "brand": "Kia",
        "model": "K5",
        "year": 2024,
        "category_id": car.category_id,
        "transmission": "automatic",
        "fuel": "petrol",
        "seats": 5,
        "price_per_day": "25000",
        "deposit": "80000",
    }
    created = await client.post("/api/v1/admin/cars", headers=admin_headers, json=payload)
    assert created.status_code == 201, created.text
    car_id = created.json()["id"]

    updated = await client.patch(
        f"/api/v1/admin/cars/{car_id}",
        headers=admin_headers,
        json={"price_per_day": "27000", "is_active": False},
    )
    assert updated.json()["price_per_day"] == "27000.00"

    # Неактивное авто скрыто из публичного каталога, но видно админу
    assert (await client.get(f"/api/v1/cars/{car_id}")).status_code == 404
    assert (await client.get("/api/v1/admin/cars", headers=admin_headers)).json()["total"] == 2

    deleted = await client.delete(f"/api/v1/admin/cars/{car_id}", headers=admin_headers)
    assert deleted.status_code == 204


async def test_image_upload_and_delete(
    client: AsyncClient, car: Car, admin_headers: dict[str, str], tmp_path, monkeypatch
) -> None:
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "media_dir", str(tmp_path))
    response = await client.post(
        f"/api/v1/admin/cars/{car.id}/images",
        headers=admin_headers,
        files={"file": ("car.webp", b"RIFF....WEBP", "image/webp")},
    )
    assert response.status_code == 200, response.text
    image = response.json()["images"][0]
    assert image["url"].startswith("/media/cars/")
    assert len(list((tmp_path / "cars").iterdir())) == 1

    bad = await client.post(
        f"/api/v1/admin/cars/{car.id}/images",
        headers=admin_headers,
        files={"file": ("x.gif", b"GIF89a", "image/gif")},
    )
    assert bad.status_code == 400

    response = await client.delete(
        f"/api/v1/admin/cars/{car.id}/images/{image['id']}", headers=admin_headers
    )
    assert response.json()["images"] == []
    assert list((tmp_path / "cars").iterdir()) == []


async def test_booking_status_flow(
    client: AsyncClient,
    car: Car,
    make_booking,
    admin_headers: dict[str, str],
    future: date,
) -> None:
    booking_id = (await make_booking(car, future, 2)).id
    url = f"/api/v1/admin/bookings/{booking_id}/status"

    bad = await client.patch(url, headers=admin_headers, json={"status": "completed"})
    assert bad.status_code == 400

    for status in ("confirmed", "active", "completed"):
        response = await client.patch(url, headers=admin_headers, json={"status": status})
        assert response.status_code == 200, response.text
        assert response.json()["status"] == status

    listing = await client.get(
        "/api/v1/admin/bookings", headers=admin_headers, params={"status": "completed"}
    )
    assert listing.json()[0]["user"]["email"] == "client@example.com"


async def test_cannot_delete_car_with_bookings(
    client: AsyncClient,
    car: Car,
    make_booking,
    admin_headers: dict[str, str],
    future: date,
) -> None:
    await make_booking(car, future, 1)
    response = await client.delete(f"/api/v1/admin/cars/{car.id}", headers=admin_headers)
    assert response.status_code == 409


async def test_users_list(
    client: AsyncClient, auth_headers: dict[str, str], admin_headers: dict[str, str]
) -> None:
    response = await client.get("/api/v1/admin/users", headers=admin_headers)
    assert {u["email"] for u in response.json()} == {"client@example.com", "admin@example.com"}
