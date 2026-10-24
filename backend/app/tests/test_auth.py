from httpx import AsyncClient


async def test_me(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "client@example.com"
    assert data["role"] == "client"
    assert data["phone"] == "+7 (701) 123-45-67"


async def test_login_wrong_password(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/v1/auth/login", json={"email": "client@example.com", "password": "wrong-pass"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Неверный email или пароль"


async def test_refresh_flow(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    login = await client.post(
        "/api/v1/auth/login", json={"email": "client@example.com", "password": "password123"}
    )
    refresh_token = login.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert response.json()["access_token"]

    # access-токен нельзя использовать как refresh
    access = login.json()["access_token"]
    response = await client.post("/api/v1/auth/refresh", json={"refresh_token": access})
    assert response.status_code == 401


async def test_me_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Требуется авторизация"


async def test_registration_removed(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "a@b.kz",
            "password": "password123",
            "full_name": "Имя",
            "phone": "87011234567",
        },
    )
    assert response.status_code in (404, 405)
