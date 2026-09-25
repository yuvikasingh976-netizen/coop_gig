from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, UserRole
from app.models.worker import Worker
from app.models.welfare import WorkerWelfare

from app.schemas.welfare import WelfareCreate, WelfareResponse


router = APIRouter(
    prefix="/welfare",
    tags=["Worker Welfare"]
)


# ---------------------------------------------------------
# CREATE WELFARE RECORD
# ---------------------------------------------------------

@router.post(
    "/",
    response_model=WelfareResponse,
    status_code=status.HTTP_201_CREATED
)
def create_welfare_record(
    welfare_data: WelfareCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can create welfare records"
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

    existing = db.scalar(
        select(WorkerWelfare).where(
            WorkerWelfare.worker_id == worker.id
        )
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Welfare record already exists"
        )

    welfare = WorkerWelfare(
        worker_id=worker.id,
        insurance_provider=welfare_data.insurance_provider,
        policy_number=welfare_data.policy_number,
        coverage_amount=welfare_data.coverage_amount,
        welfare_contribution=welfare_data.welfare_contribution,
        emergency_support=welfare_data.emergency_support,
        notes=welfare_data.notes
    )

    db.add(welfare)
    db.commit()
    db.refresh(welfare)

    return welfare


# ---------------------------------------------------------
# GET MY WELFARE RECORD
# ---------------------------------------------------------

@router.get(
    "/me",
    response_model=WelfareResponse
)
def get_my_welfare(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can access this endpoint"
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

    welfare = db.scalar(
        select(WorkerWelfare).where(
            WorkerWelfare.worker_id == worker.id
        )
    )

    if not welfare:
        raise HTTPException(
            status_code=404,
            detail="Welfare record not found"
        )

    return welfare


# ---------------------------------------------------------
# UPDATE MY WELFARE RECORD
# ---------------------------------------------------------

@router.patch(
    "/me",
    response_model=WelfareResponse
)
def update_my_welfare(
    welfare_data: WelfareCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can update welfare records"
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

    welfare = db.scalar(
        select(WorkerWelfare).where(
            WorkerWelfare.worker_id == worker.id
        )
    )

    if not welfare:
        raise HTTPException(
            status_code=404,
            detail="Welfare record not found"
        )

    welfare.insurance_provider = welfare_data.insurance_provider
    welfare.policy_number = welfare_data.policy_number
    welfare.coverage_amount = welfare_data.coverage_amount
    welfare.welfare_contribution = welfare_data.welfare_contribution
    welfare.emergency_support = welfare_data.emergency_support
    welfare.notes = welfare_data.notes

    db.commit()
    db.refresh(welfare)

    return welfare


# ---------------------------------------------------------
# ADMIN: VIEW WORKER WELFARE
# ---------------------------------------------------------

@router.get(
    "/worker/{worker_id}",
    response_model=WelfareResponse
)
def get_worker_welfare(
    worker_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in [
        UserRole.ADMIN,
        UserRole.COOPERATIVE_ADMIN
    ]:
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

    welfare = db.scalar(
        select(WorkerWelfare).where(
            WorkerWelfare.worker_id == worker_id
        )
    )

    if not welfare:
        raise HTTPException(
            status_code=404,
            detail="Welfare record not found"
        )

    return welfare