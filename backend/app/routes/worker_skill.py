from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.service import Service
from app.models.user import User, UserRole
from app.models.worker import Worker
from app.models.worker_skill import WorkerSkill
from app.schemas.worker_skill import (
    WorkerSkillCreate,
    WorkerSkillResponse,
)


router = APIRouter(
    prefix="/worker-skills",
    tags=["Worker Skills"]
)


@router.post(
    "/",
    response_model=WorkerSkillResponse
)
def add_worker_skill(
    skill_data: WorkerSkillCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can add skills"
        )

    worker = db.scalar(
        select(Worker).where(
            Worker.user_id == current_user.id
        )
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker profile not found"
        )

    service = db.get(
        Service,
        skill_data.service_id
    )

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    existing_skill = db.scalar(
        select(WorkerSkill).where(
            WorkerSkill.worker_id == worker.id,
            WorkerSkill.service_id == skill_data.service_id
        )
    )

    if existing_skill:
        raise HTTPException(
            status_code=400,
            detail="Worker already has this skill"
        )

    worker_skill = WorkerSkill(
        worker_id=worker.id,
        service_id=skill_data.service_id,
        skill_level=skill_data.skill_level,
        years_experience=skill_data.years_experience
    )

    db.add(worker_skill)
    db.commit()
    db.refresh(worker_skill)

    return worker_skill


@router.get(
    "/me",
    response_model=list[WorkerSkillResponse]
)
def get_my_skills(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    worker = db.scalar(
        select(Worker).where(
            Worker.user_id == current_user.id
        )
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker profile not found"
        )

    skills = db.scalars(
        select(WorkerSkill).where(
            WorkerSkill.worker_id == worker.id
        )
    ).all()

    return skills