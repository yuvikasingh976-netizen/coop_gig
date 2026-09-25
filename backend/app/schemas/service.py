from pydantic import BaseModel, Field


class ServiceCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=100
    )

    description: str | None = None

    category: str = Field(
        min_length=2,
        max_length=100
    )

    base_price: float = Field(
        default=0,
        ge=0
    )


class ServiceResponse(BaseModel):

    id: int
    name: str
    description: str | None
    category: str
    base_price: float
    is_active: bool

    model_config = {
        "from_attributes": True
    }