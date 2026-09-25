from pydantic import BaseModel


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str
    payment_id: int
    booking_id: int
    customer_id: int
    worker_id: int
    amount: float
    status: str

    model_config = {
        "from_attributes": True
    }