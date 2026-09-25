from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    booking_id: int

    rating: int = Field(
        ge=1,
        le=5
    )

    comment: str | None = None


class ReviewResponse(BaseModel):
    id: int
    booking_id: int
    customer_id: int
    worker_id: int
    rating: int
    comment: str | None

    model_config = {
        "from_attributes": True
    }