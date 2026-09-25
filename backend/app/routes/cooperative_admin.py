from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, UserRole
from app.models.worker import Worker, VerificationStatus
from app.models.cooperative import Cooperative
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus


router = APIRouter(
    prefix="/cooperative-admin",
    tags=["Cooperative Admin"]
)


# =========================================================
# HELPER
# =========================================================

def get_cooperative_admin_access(
    current_user: User,
    db: Session
):
    """
    Verify that the logged-in user is a Cooperative Admin
    and return the cooperative they manage.
    """

    if current_user.role != UserRole.COOPERATIVE_ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Cooperative admin access required"
        )

    if current_user.cooperative_id is None:
        raise HTTPException(
            status_code=400,
            detail="Cooperative admin is not associated with a cooperative"
        )

    cooperative = db.scalar(
        select(Cooperative).where(
            Cooperative.id == current_user.cooperative_id
        )
    )

    if not cooperative:
        raise HTTPException(
            status_code=404,
            detail="Cooperative not found"
        )

    return cooperative


# =========================================================
# COOPERATIVE ADMIN DASHBOARD
# =========================================================

@router.get("/dashboard")
def cooperative_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cooperative = get_cooperative_admin_access(
        current_user,
        db
    )

    cooperative_id = cooperative.id

    # Total workers
    total_workers = db.scalar(
        select(func.count(Worker.id)).where(
            Worker.cooperative_id == cooperative_id
        )
    ) or 0

    # Verified workers
    verified_workers = db.scalar(
        select(func.count(Worker.id)).where(
            Worker.cooperative_id == cooperative_id,
            Worker.verification_status == VerificationStatus.VERIFIED
        )
    ) or 0

    # Pending workers
    pending_workers = db.scalar(
        select(func.count(Worker.id)).where(
            Worker.cooperative_id == cooperative_id,
            Worker.verification_status == VerificationStatus.PENDING
        )
    ) or 0

    # Rejected workers
    rejected_workers = db.scalar(
        select(func.count(Worker.id)).where(
            Worker.cooperative_id == cooperative_id,
            Worker.verification_status == VerificationStatus.REJECTED
        )
    ) or 0

    # Total bookings
    total_bookings = db.scalar(
        select(func.count(Booking.id))
        .join(
            Worker,
            Worker.id == Booking.worker_id
        )
        .where(
            Worker.cooperative_id == cooperative_id
        )
    ) or 0

    # Completed bookings
    completed_bookings = db.scalar(
        select(func.count(Booking.id))
        .join(
            Worker,
            Worker.id == Booking.worker_id
        )
        .where(
            Worker.cooperative_id == cooperative_id,
            Booking.status == BookingStatus.COMPLETED
        )
    ) or 0

    # Successful payments / revenue
    total_revenue = db.scalar(
        select(
            func.coalesce(
                func.sum(Payment.amount),
                0
            )
        )
        .join(
            Worker,
            Worker.id == Payment.worker_id
        )
        .where(
            Worker.cooperative_id == cooperative_id,
            Payment.status == PaymentStatus.SUCCESS
        )
    ) or 0

    return {
        "cooperative_id": cooperative.id,
        "cooperative_name": cooperative.name,
        "total_workers": total_workers,
        "verified_workers": verified_workers,
        "pending_workers": pending_workers,
        "rejected_workers": rejected_workers,
        "total_bookings": total_bookings,
        "completed_bookings": completed_bookings,
        "total_revenue": float(total_revenue)
    }


# =========================================================
# VIEW ALL WORKERS OF THIS COOPERATIVE
# =========================================================

@router.get("/workers")
def get_cooperative_workers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cooperative = get_cooperative_admin_access(
        current_user,
        db
    )

    workers = db.scalars(
        select(Worker)
        .where(
            Worker.cooperative_id == cooperative.id
        )
        .order_by(
            Worker.created_at.desc()
        )
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
            "bio": worker.bio,
            "hourly_rate": worker.hourly_rate,
            "availability": worker.availability,
            "verification_status": (
                worker.verification_status.value
            ),
            "average_rating": worker.average_rating,
            "total_jobs": worker.total_jobs,
            "latitude": worker.latitude,
            "longitude": worker.longitude
        })

    return result


# =========================================================
# VERIFY WORKER
# =========================================================

@router.patch("/workers/{worker_id}/verify")
def verify_worker(
    worker_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cooperative = get_cooperative_admin_access(
        current_user,
        db
    )

    worker = db.scalar(
        select(Worker).where(
            Worker.id == worker_id,
            Worker.cooperative_id == cooperative.id
        )
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found in your cooperative"
        )

    worker.verification_status = VerificationStatus.VERIFIED

    db.commit()
    db.refresh(worker)

    return {
        "message": "Worker verified successfully",
        "worker_id": worker.id,
        "verification_status": worker.verification_status.value
    }


# =========================================================
# REJECT WORKER
# =========================================================

@router.patch("/workers/{worker_id}/reject")
def reject_worker(
    worker_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    cooperative = get_cooperative_admin_access(
        current_user,
        db
    )

    worker = db.scalar(
        select(Worker).where(
            Worker.id == worker_id,
            Worker.cooperative_id == cooperative.id
        )
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found in your cooperative"
        )

    worker.verification_status = VerificationStatus.REJECTED

    db.commit()
    db.refresh(worker)

    return {
        "message": "Worker rejected",
        "worker_id": worker.id,
        "verification_status": worker.verification_status.value
    }