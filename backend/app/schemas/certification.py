from pydantic import BaseModel, Field


class CertificationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    issuing_organization: str = Field(min_length=2, max_length=150)
    certificate_number: str | None = Field(default=None, max_length=100)
    issue_date: str | None = None
    expiry_date: str | None = None
    description: str | None = None


class CertificationResponse(BaseModel):
    id: int
    worker_id: int
    name: str
    issuing_organization: str
    certificate_number: str | None
    issue_date: str | None
    expiry_date: str | None
    description: str | None
    is_verified: bool

    model_config = {"from_attributes": True}