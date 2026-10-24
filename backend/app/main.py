from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.services.payments import get_payment_provider

VALIDATION_MESSAGES = {
    "missing": "обязательное поле",
    "string_too_short": "слишком короткое значение",
    "string_too_long": "слишком длинное значение",
    "value_error": "некорректное значение",
    "date_from_datetime_parsing": "некорректная дата",
    "date_parsing": "некорректная дата",
    "int_parsing": "ожидается целое число",
    "decimal_parsing": "ожидается число",
    "enum": "недопустимое значение",
    "greater_than": "значение слишком маленькое",
    "greater_than_equal": "значение слишком маленькое",
    "less_than_equal": "значение слишком большое",
}


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    errors = exc.errors()
    first = errors[0] if errors else {}
    message = str(first.get("msg", ""))
    if first.get("type") == "value_error" and message.startswith("Value error, "):
        # Сообщение из нашего валидатора — уже на русском
        detail = message.removeprefix("Value error, ")
    else:
        field = ".".join(str(p) for p in first.get("loc", ())[1:]) or "запрос"
        reason = VALIDATION_MESSAGES.get(str(first.get("type")), "некорректное значение")
        detail = f"Поле «{field}»: {reason}"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": detail, "errors": jsonable_encoder(errors)},
    )


def create_app() -> FastAPI:
    settings = get_settings()
    # Падаем на старте, если провайдер оплаты не настроен (или mock в production)
    get_payment_provider()

    app = FastAPI(
        title="Joker Auto Rent API",
        description="Аренда авто в Алматы",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.frontend_url],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.include_router(api_router, prefix="/api/v1")

    media_dir = Path(settings.media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=media_dir), name="media")

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
