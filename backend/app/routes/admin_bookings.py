from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, UserRole
from app.models.worker import Worker
from app.models.booking import Booking


router = APIRouter(
    prefix="/admin/bookings",
    tags=["Admin - Bookings"]
)


# ---------------------------------------------------------
# VIEW ALL BOOKINGS
# ---------------------------------------------------------

@router.get("/")
def get_all_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    bookings = db.scalars(
        select(Booking).order_by(
            Booking.created_at.desc()
        )
    ).all()

    result = []

    for booking in bookings:

        customer = db.scalar(
            select(User).where(
                User.id == booking.customer_id
            )
        )

        worker = db.scalar(
            select(Worker).where(
                Worker.id == booking.worker_id
            )
        )

        worker_user = None

        if worker:
            worker_user = db.scalar(
                select(User).where(
                    User.id == worker.user_id
                )
            )

        result.append({
            "booking_id": booking.id,

            "customer_id": booking.customer_id,
            "customer_name": (
                customer.name
                if customer
                else None
            ),

            "worker_id": booking.worker_id,
            "worker_name": (
                worker_user.name
                if worker_user
                else None
            ),

            "service_id": booking.service_id,

            "scheduled_date": booking.scheduled_date,
            "scheduled_time": booking.scheduled_time,

            "address": booking.address,
            "city": booking.city,
            "description": booking.description,

            "estimated_amount": booking.estimated_amount,

            "status": booking.status.value,

            "created_at": booking.created_at
        })

    return result