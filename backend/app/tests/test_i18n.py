import ast
import re
from pathlib import Path

from httpx import AsyncClient

from app.core.i18n import KK, parse_lang, translate

APP_DIR = Path(__file__).resolve().parents[1]
CYRILLIC = re.compile(r"[А-Яа-яЁё]")
ERROR_CALLS = {"HTTPException", "ValueError"}


def user_facing_messages() -> set[str]:
    """Русские строки из HTTPException/ValueError и констант *_DETAIL во всём app/."""
    found: set[str] = set()
    for path in APP_DIR.rglob("*.py"):
        if "tests" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                if name in ERROR_CALLS:
                    for arg in node.args:
                        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                            found.add(arg.value)
            elif isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
                targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
                value = node.value.value
                if any(t.endswith("_DETAIL") for t in targets) and isinstance(value, str):
                    found.add(value)
    return {m for m in found if CYRILLIC.search(m)}


def test_every_error_message_has_kazakh_translation() -> None:
    messages = user_facing_messages()
    assert len(messages) > 10
    missing = sorted(m for m in messages if translate(m, "kk") == m)
    assert missing == []


def test_dynamic_messages_are_translated() -> None:
    assert translate("Нельзя перевести бронь из статуса «pending» в «completed»", "kk") == (
        "Брондауды «pending» мәртебесінен «completed» мәртебесіне ауыстыруға болмайды"
    )


def test_parse_lang() -> None:
    assert parse_lang("kk") == "kk"
    assert parse_lang("kk-KZ,ru;q=0.8") == "kk"
    assert parse_lang("ru") == "ru"
    assert parse_lang("en-US") == "ru"
    assert parse_lang(None) == "ru"


async def test_api_error_in_kazakh(client: AsyncClient) -> None:
    body = {"email": "nobody@example.com", "password": "wrongpass1"}
    kk = await client.post("/api/v1/auth/login", json=body, headers={"Accept-Language": "kk"})
    ru = await client.post("/api/v1/auth/login", json=body)

    assert kk.status_code == ru.status_code == 401
    assert kk.json()["detail"] == KK["Неверный email или пароль"]
    assert ru.json()["detail"] == "Неверный email или пароль"


async def test_auth_header_kept_on_translated_401(client: AsyncClient) -> None:
    response = await client.get("/api/v1/auth/me", headers={"Accept-Language": "kk"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Авторизация қажет"
    assert response.headers["www-authenticate"] == "Bearer"


async def test_validation_error_in_kazakh(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login", json={"email": "a@b.kz"}, headers={"Accept-Language": "kk"}
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "«password» өрісі: міндетті өріс"
