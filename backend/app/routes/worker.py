from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.cooperative import Cooperative
from app.models.user import User, UserRole
from app.models.worker import Worker, VerificationStatus
from app.schemas.worker import (
    WorkerProfileCreate,
    WorkerResponse,
)


router = APIRouter(
    prefix="/workers",
    tags=["Workers"]
)


@router.post(
    "/profile",
    response_model=WorkerResponse
)
def create_worker_profile(
    worker_data: WorkerProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can create worker profiles"
        )

    existing_worker = db.scalar(
        select(Worker).where(
            Worker.user_id == current_user.id
        )
    )

    if existing_worker:
        raise HTTPException(
            status_code=400,
            detail="Worker profile already exists"
        )

    cooperative = db.get(
        Cooperative,
        worker_data.cooperative_id
    )

    if not cooperative:
        raise HTTPException(
            status_code=404,
            detail="Cooperative not found"
        )

    worker = Worker(
        user_id=current_user.id,
        cooperative_id=worker_data.cooperative_id,
        experience_years=worker_data.experience_years,
        bio=worker_data.bio,
        hourly_rate=worker_data.hourly_rate,
        latitude=worker_data.latitude,
        longitude=worker_data.longitude,
        availability=True,
        verification_status=VerificationStatus.PENDING
    )

    db.add(worker)
    db.commit()
    db.refresh(worker)

    return worker


@router.get(
    "/me",
    response_model=WorkerResponse
)
def get_my_worker_profile(
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

    return worker
# =========================================================
# GET CURRENT WORKER PROFILE
# =========================================================

@router.get("/me")
def get_my_worker_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    worker = db.scalar(
        select(Worker).where(
            Worker.user_id == current_user.id
        )
    )

    if worker is None:
        raise HTTPException(
            status_code=404,
            detail="Worker profile not found"
        )

    return {
        "id": worker.id,
        "user_id": worker.user_id,
        "name": current_user.name,
        "email": current_user.email,
        "phone": current_user.phone,
        "cooperative_id": worker.cooperative_id,
        "experience_years": worker.experience_years,
        "bio": worker.bio,
        "hourly_rate": worker.hourly_rate,
        "latitude": worker.latitude,
        "longitude": worker.longitude,
        "availability": worker.availability,
        "verification_status": worker.verification_status.value,
        "average_rating": worker.average_rating,
        "total_jobs": worker.total_jobs
    }