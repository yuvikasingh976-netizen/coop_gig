from pydantic import BaseModel, EmailStr, Field


class CooperativeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)

    registration_number: str = Field(
        min_length=2,
        max_length=100
    )

    address: str = Field(
        min_length=5,
        max_length=300
    )

    city: str
    state: str

    phone: str = Field(
        min_length=10,
        max_length=20
    )

    email: EmailStr


class CooperativeResponse(CooperativeCreate):
    id: int
    is_active: bool

    model_config = {
        "from_attributes": True
    }