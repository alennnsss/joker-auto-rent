from fastapi import APIRouter

from app.core.deps import AppSettings, Provider
from app.schemas.payment import PublicConfigOut

router = APIRouter(tags=["config"])


@router.get("/config", response_model=PublicConfigOut)
async def get_config(settings: AppSettings, provider: Provider) -> PublicConfigOut:
    """Публичные настройки для фронтенда. Провайдер оплаты наружу не раскрывается."""
    return PublicConfigOut(
        currency=settings.currency,
        timezone=settings.timezone,
        online_payment_enabled=provider.supports_online,
    )
