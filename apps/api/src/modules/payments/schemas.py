from pydantic import BaseModel


class PaymentResponse(BaseModel):
    payment_id: int
    order_id: int
    provider: str = "mock"
    status: str
    amount_cents: int
    currency: str
    idempotency_key: str | None = None
