from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass
from decimal import Decimal

from app.core.config import Settings
from app.models import Booking, Payment, PaymentStatus


class PaymentProviderError(Exception):
    """Ошибка на стороне провайдера; сообщение показывается пользователю."""


@dataclass(frozen=True)
class PaymentInit:
    provider_payment_id: str
    redirect_url: str
    # Некоторые провайдеры (mock) подтверждают оплату сразу, без webhook
    status: PaymentStatus = PaymentStatus.PENDING


@dataclass(frozen=True)
class PaymentEvent:
    provider_payment_id: str
    status: PaymentStatus


class PaymentProvider(ABC):
    """Абстракция платёжного провайдера. Роутеры и фронтенд знают только о ней."""

    name: str
    supports_online: bool = True

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @abstractmethod
    async def create_payment(self, booking: Booking, amount: Decimal) -> PaymentInit: ...

    @abstractmethod
    def verify_webhook(self, headers: Mapping[str, str], body: bytes) -> bool: ...

    @abstractmethod
    def parse_webhook(self, body: bytes) -> PaymentEvent:
        """Бросает ValueError, если тело webhook невалидно."""

    @abstractmethod
    async def refund(self, payment: Payment) -> None: ...
