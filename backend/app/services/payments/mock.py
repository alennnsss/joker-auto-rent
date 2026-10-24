import json
from collections.abc import Mapping
from decimal import Decimal
from uuid import uuid4

from app.core.config import Settings
from app.models import Booking, Payment, PaymentStatus
from app.services.payments.base import PaymentEvent, PaymentInit, PaymentProvider


class MockPaymentProvider(PaymentProvider):
    """Тестовый провайдер для разработки: оплата проходит мгновенно. Запрещён в production."""

    name = "mock"

    def __init__(self, settings: Settings) -> None:
        if settings.is_production:
            raise RuntimeError("MockPaymentProvider is forbidden when ENV=production")
        super().__init__(settings)

    async def create_payment(self, booking: Booking, amount: Decimal) -> PaymentInit:
        return PaymentInit(
            provider_payment_id=f"mock_{uuid4().hex}",
            redirect_url=f"{self.settings.frontend_url}/payment/success?booking={booking.id}",
            status=PaymentStatus.SUCCEEDED,
        )

    def verify_webhook(self, headers: Mapping[str, str], body: bytes) -> bool:
        return True

    def parse_webhook(self, body: bytes) -> PaymentEvent:
        # Формат: {"payment_id": "mock_...", "status": "succeeded"}
        try:
            data = json.loads(body)
            return PaymentEvent(
                provider_payment_id=str(data["payment_id"]),
                status=PaymentStatus(data["status"]),
            )
        except (ValueError, KeyError, TypeError) as exc:
            raise ValueError("Invalid mock webhook body") from exc

    async def refund(self, payment: Payment) -> None:
        return None
