from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.i18n import parse_lang, translate, validation_detail


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)
    # detail из сервисов — на русском, переводим на язык интерфейса
    detail = exc.detail
    if isinstance(detail, str):
        detail = translate(detail, parse_lang(request.headers.get("accept-language")))
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
        headers=getattr(exc, "headers", None),
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    lang = parse_lang(request.headers.get("accept-language"))
    errors = exc.errors()
    first = errors[0] if errors else {}
    message = str(first.get("msg", ""))
    if first.get("type") == "value_error" and message.startswith("Value error, "):
        # Сообщение из нашего валидатора — на русском, переводим по словарю
        detail = translate(message.removeprefix("Value error, "), lang)
    else:
        field = ".".join(str(p) for p in first.get("loc", ())[1:])
        detail = validation_detail(field, str(first.get("type")), lang)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": detail, "errors": jsonable_encoder(errors)},
    )


def create_app() -> FastAPI:
    settings = get_settings()

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
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.include_router(api_router, prefix="/api/v1")

    media_dir = Path(settings.media_dir)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=media_dir), name="media")

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
