from pydantic import BaseModel, Field

from app.models.payment import PaymentMethod, PaymentStatus


class PaymentCreate(BaseModel):
    booking_id: int
    payment_method: PaymentMethod


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    customer_id: int
    worker_id: int
    amount: float
    payment_method: PaymentMethod
    status: PaymentStatus
    transaction_id: str | None

    model_config = {
        "from_attributes": True
    }