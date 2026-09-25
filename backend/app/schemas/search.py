from pydantic import BaseModel


class WorkerSearchResponse(BaseModel):
    worker_id: int
    user_id: int
    name: str

    service_id: int
    service_name: str

    skill_level: str
    years_experience: int

    hourly_rate: float

    latitude: float | None
    longitude: float | None

    distance_km: float | None

    availability: bool
    verification_status: str

    average_rating: float
    total_jobs: int