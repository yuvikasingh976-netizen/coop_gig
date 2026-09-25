from pydantic import BaseModel, Field


class WelfareCreate(BaseModel):
    insurance_provider: str | None = Field(default=None, max_length=150)
    policy_number: str | None = Field(default=None, max_length=100)

    coverage_amount: float = Field(default=0, ge=0)
    welfare_contribution: float = Field(default=0, ge=0)
    emergency_support: float = Field(default=0, ge=0)

    notes: str | None = None


class WelfareResponse(BaseModel):
    id: int
    worker_id: int

    insurance_provider: str | None
    policy_number: str | None

    coverage_amount: float
    welfare_contribution: float
    emergency_support: float

    notes: str | None
    is_active: bool

    model_config = {
        "from_attributes": True
    }