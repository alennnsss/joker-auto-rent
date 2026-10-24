from collections.abc import Mapping
from decimal import Decimal

from app.models import Booking, Payment
from app.services.payments.base import (
    PaymentEvent,
    PaymentInit,
    PaymentProvider,
    PaymentProviderError,
)


class CashPaymentProvider(PaymentProvider):
    """Только оплата при получении: онлайн-платежей и webhook нет."""

    name = "cash"
    supports_online = False

    async def create_payment(self, booking: Booking, amount: Decimal) -> PaymentInit:
        raise PaymentProviderError("Онлайн-оплата пока недоступна")

    def verify_webhook(self, headers: Mapping[str, str], body: bytes) -> bool:
        return False

    def parse_webhook(self, body: bytes) -> PaymentEvent:
        raise ValueError("Cash provider has no webhooks")

    async def refund(self, payment: Payment) -> None:
        return None
