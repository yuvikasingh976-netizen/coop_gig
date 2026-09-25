from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, UserRole
from app.models.worker import Worker, VerificationStatus


router = APIRouter(
    prefix="/admin/workers",
    tags=["Admin - Workers"]
)


# ---------------------------------------------------------
# VIEW ALL WORKERS
# ---------------------------------------------------------

@router.get("/")
def get_all_workers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    workers = db.scalars(
        select(Worker).order_by(Worker.created_at.desc())
    ).all()

    result = []

    for worker in workers:
        user = db.scalar(
            select(User).where(
                User.id == worker.user_id
            )
        )

        result.append({
            "worker_id": worker.id,
            "user_id": worker.user_id,
            "name": user.name if user else None,
            "email": user.email if user else None,
            "phone": user.phone if user else None,
            "experience_years": worker.experience_years,
            "hourly_rate": worker.hourly_rate,
            "availability": worker.availability,
            "verification_status": worker.verification_status.value,
            "average_rating": worker.average_rating,
            "total_jobs": worker.total_jobs,
            "latitude": worker.latitude,
            "longitude": worker.longitude
        })

    return result


# ---------------------------------------------------------
# VERIFY WORKER
# ---------------------------------------------------------

@router.patch("/{worker_id}/verify")
def verify_worker(
    worker_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    worker = db.scalar(
        select(Worker).where(
            Worker.id == worker_id
        )
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    worker.verification_status = VerificationStatus.VERIFIED

    db.commit()
    db.refresh(worker)

    return {
        "message": "Worker verified successfully",
        "worker_id": worker.id,
        "verification_status": worker.verification_status.value
    }


# ---------------------------------------------------------
# REJECT WORKER
# ---------------------------------------------------------

@router.patch("/{worker_id}/reject")
def reject_worker(
    worker_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    worker = db.scalar(
        select(Worker).where(
            Worker.id == worker_id
        )
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    worker.verification_status = VerificationStatus.REJECTED

    db.commit()
    db.refresh(worker)

    return {
        "message": "Worker rejected",
        "worker_id": worker.id,
        "verification_status": worker.verification_status.value
    }