from pydantic import BaseModel, Field

from app.models.worker import VerificationStatus


class WorkerProfileCreate(BaseModel):

    cooperative_id: int

    experience_years: int = Field(
        default=0,
        ge=0,
        le=60
    )

    bio: str | None = None

    hourly_rate: float = Field(
        default=0,
        ge=0
    )

    latitude: float | None = None

    longitude: float | None = None


class WorkerResponse(BaseModel):

    id: int
    user_id: int
    cooperative_id: int

    experience_years: int
    bio: str | None

    hourly_rate: float

    latitude: float | None
    longitude: float | None

    availability: bool

    verification_status: VerificationStatus

    average_rating: float
    total_jobs: int

    model_config = {
        "from_attributes": True
    }