from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, UserRole
from app.models.worker import Worker
from app.models.service import Service
from app.models.worker_skill import WorkerSkill
from app.models.booking import Booking, BookingStatus

from app.schemas.booking import (
    BookingCreate,
    BookingResponse
)


router = APIRouter(
    prefix="/bookings",
    tags=["Bookings"]
)


# ============================================================
# CUSTOMER - CREATE BOOKING
# ============================================================

@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED
)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only customers can create bookings
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can create bookings"
        )

    # Check worker exists
    worker = db.get(
        Worker,
        booking_data.worker_id
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    # Check worker availability
    if not worker.availability:
        raise HTTPException(
            status_code=400,
            detail="Worker is currently unavailable"
        )

    # Check service exists
    service = db.get(
        Service,
        booking_data.service_id
    )

    if not service:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    # Check worker provides this service
    worker_skill = db.scalar(
        select(WorkerSkill).where(
            WorkerSkill.worker_id == worker.id,
            WorkerSkill.service_id == service.id
        )
    )

    if not worker_skill:
        raise HTTPException(
            status_code=400,
            detail="Worker does not provide this service"
        )

    # Use worker's hourly rate as estimated amount
    estimated_amount = worker.hourly_rate

    # Create booking
    booking = Booking(
        customer_id=current_user.id,
        worker_id=worker.id,
        service_id=service.id,
        scheduled_date=booking_data.scheduled_date,
        scheduled_time=booking_data.scheduled_time,
        address=booking_data.address,
        city=booking_data.city,
        description=booking_data.description,
        estimated_amount=estimated_amount,
        status=BookingStatus.PENDING
    )

    db.add(booking)
    db.commit()
    db.refresh(booking)

    return booking


# ============================================================
# CUSTOMER - VIEW MY BOOKINGS
# ============================================================

@router.get(
    "/my",
    response_model=list[BookingResponse]
)
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can view customer bookings"
        )

    bookings = db.scalars(
        select(Booking)
        .where(
            Booking.customer_id == current_user.id
        )
        .order_by(Booking.created_at.desc())
    ).all()

    return bookings


# ============================================================
# WORKER - VIEW INCOMING BOOKINGS
# ============================================================

@router.get(
    "/worker",
    response_model=list[BookingResponse]
)
def get_worker_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can view worker bookings"
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

    bookings = db.scalars(
        select(Booking)
        .where(
            Booking.worker_id == worker.id
        )
        .order_by(Booking.created_at.desc())
    ).all()

    return bookings


# ============================================================
# WORKER - ACCEPT BOOKING
# ============================================================

@router.patch(
    "/{booking_id}/accept",
    response_model=BookingResponse
)
def accept_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can accept bookings"
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

    booking = db.get(
        Booking,
        booking_id
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # Make sure booking belongs to this worker
    if booking.worker_id != worker.id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this booking"
        )

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending bookings can be accepted"
        )

    booking.status = BookingStatus.ACCEPTED

    db.commit()
    db.refresh(booking)

    return booking


# ============================================================
# WORKER - REJECT BOOKING
# ============================================================

@router.patch(
    "/{booking_id}/reject",
    response_model=BookingResponse
)
def reject_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can reject bookings"
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

    booking = db.get(
        Booking,
        booking_id
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.worker_id != worker.id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this booking"
        )

    if booking.status != BookingStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending bookings can be rejected"
        )

    booking.status = BookingStatus.REJECTED

    db.commit()
    db.refresh(booking)

    return booking


# ============================================================
# WORKER - START JOB
# ============================================================

@router.patch(
    "/{booking_id}/start",
    response_model=BookingResponse
)
def start_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can start bookings"
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

    booking = db.get(
        Booking,
        booking_id
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.worker_id != worker.id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this booking"
        )

    if booking.status != BookingStatus.ACCEPTED:
        raise HTTPException(
            status_code=400,
            detail="Only accepted bookings can be started"
        )

    booking.status = BookingStatus.IN_PROGRESS

    db.commit()
    db.refresh(booking)

    return booking


# ============================================================
# WORKER - COMPLETE JOB
# ============================================================

@router.patch(
    "/{booking_id}/complete",
    response_model=BookingResponse
)
def complete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can complete bookings"
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

    booking = db.get(
        Booking,
        booking_id
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.worker_id != worker.id:
        raise HTTPException(
            status_code=403,
            detail="You are not assigned to this booking"
        )

    if booking.status != BookingStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=400,
            detail="Only in-progress bookings can be completed"
        )

    booking.status = BookingStatus.COMPLETED

    # Increase worker's completed job count
    worker.total_jobs += 1

    db.commit()
    db.refresh(booking)

    return booking