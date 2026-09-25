from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, UserRole
from app.models.worker import Worker
from app.models.cooperative import Cooperative
from app.models.service import Service
from app.models.booking import Booking
from app.models.payment import Payment, PaymentStatus
from app.models.review import Review


router = APIRouter(
    prefix="/admin",
    tags=["Admin Dashboard"]
)


@router.get("/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only ADMIN can access the dashboard
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    total_users = db.scalar(
        select(func.count(User.id))
    ) or 0

    total_workers = db.scalar(
        select(func.count(Worker.id))
    ) or 0

    total_cooperatives = db.scalar(
        select(func.count(Cooperative.id))
    ) or 0

    total_services = db.scalar(
        select(func.count(Service.id))
    ) or 0

    total_bookings = db.scalar(
        select(func.count(Booking.id))
    ) or 0

    completed_bookings = db.scalar(
        select(func.count(Booking.id)).where(
            Booking.status == "COMPLETED"
        )
    ) or 0

    successful_payments = db.scalar(
        select(func.count(Payment.id)).where(
            Payment.status == PaymentStatus.SUCCESS
        )
    ) or 0

    total_revenue = db.scalar(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.status == PaymentStatus.SUCCESS
        )
    ) or 0

    average_rating = db.scalar(
        select(func.avg(Review.rating))
    )

    return {
        "total_users": total_users,
        "total_workers": total_workers,
        "total_cooperatives": total_cooperatives,
        "total_services": total_services,
        "total_bookings": total_bookings,
        "completed_bookings": completed_bookings,
        "successful_payments": successful_payments,
        "total_revenue": float(total_revenue),
        "average_rating": round(float(average_rating), 2)
        if average_rating is not None else 0.0
    }