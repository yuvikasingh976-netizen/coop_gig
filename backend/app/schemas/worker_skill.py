from pydantic import BaseModel, Field

from app.models.worker_skill import SkillLevel


class WorkerSkillCreate(BaseModel):

    service_id: int

    skill_level: SkillLevel = SkillLevel.BEGINNER

    years_experience: int = Field(
        default=0,
        ge=0,
        le=60
    )


class WorkerSkillResponse(BaseModel):

    id: int
    worker_id: int
    service_id: int
    skill_level: SkillLevel
    years_experience: int

    model_config = {
        "from_attributes": True
    }