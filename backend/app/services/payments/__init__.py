from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.payments.base import (
    PaymentEvent,
    PaymentInit,
    PaymentProvider,
    PaymentProviderError,
)
from app.services.payments.cash import CashPaymentProvider
from app.services.payments.mock import MockPaymentProvider

# Новый провайдер (kaspi, freedompay, halyk, cloudpayments) регистрируется здесь
PROVIDERS: dict[str, type[PaymentProvider]] = {
    "mock": MockPaymentProvider,
    "cash": CashPaymentProvider,
}


def build_payment_provider(settings: Settings) -> PaymentProvider:
    try:
        provider_cls = PROVIDERS[settings.payment_provider]
    except KeyError:
        raise RuntimeError(f"Unknown PAYMENT_PROVIDER: {settings.payment_provider!r}") from None
    return provider_cls(settings)


@lru_cache
def get_payment_provider() -> PaymentProvider:
    return build_payment_provider(get_settings())


__all__ = [
    "PaymentEvent",
    "PaymentInit",
    "PaymentProvider",
    "PaymentProviderError",
    "build_payment_provider",
    "get_payment_provider",
]
