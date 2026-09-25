from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.worker import Worker
from app.models.certification import Certification
from app.schemas.certification import (
    CertificationCreate,
    CertificationResponse
)


router = APIRouter(
    prefix="/certifications",
    tags=["Certifications"]
)


@router.post(
    "/",
    response_model=CertificationResponse
)
def add_certification(
    certification_data: CertificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can add certifications"
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

    certification = Certification(
        worker_id=worker.id,
        **certification_data.model_dump()
    )

    db.add(certification)
    db.commit()
    db.refresh(certification)

    return certification


@router.get(
    "/me",
    response_model=list[CertificationResponse]
)
def get_my_certifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can view worker certifications"
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

    certifications = db.scalars(
        select(Certification).where(
            Certification.worker_id == worker.id
        )
    ).all()

    return certifications