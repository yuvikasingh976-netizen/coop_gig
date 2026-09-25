from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    worker_id: int
    service_id: int

    scheduled_date: str = Field(
        min_length=8,
        max_length=20
    )

    scheduled_time: str = Field(
        min_length=3,
        max_length=20
    )

    address: str = Field(
        min_length=5,
        max_length=300
    )

    city: str = Field(
        min_length=2,
        max_length=100
    )

    description: str | None = None


class BookingResponse(BaseModel):
    id: int
    customer_id: int
    worker_id: int
    service_id: int

    scheduled_date: str
    scheduled_time: str

    address: str
    city: str

    description: str | None

    estimated_amount: float
    status: str

    model_config = {
        "from_attributes": True
    }