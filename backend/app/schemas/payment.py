from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models import PaymentStatus


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    booking_id: int
    amount: Decimal
    provider: str
    provider_payment_id: str
    status: PaymentStatus
    created_at: datetime


class PaymentCreateOut(BaseModel):
    payment_id: int
    status: PaymentStatus
    redirect_url: str


class PublicConfigOut(BaseModel):
    currency: str
    timezone: str
    online_payment_enabled: bool
