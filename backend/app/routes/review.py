from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, UserRole
from app.models.worker import Worker
from app.models.booking import Booking, BookingStatus
from app.models.review import Review

from app.schemas.review import (
    ReviewCreate,
    ReviewResponse
)


router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"]
)


# ============================================================
# CUSTOMER - CREATE REVIEW
# ============================================================

@router.post(
    "/",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED
)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only customers can submit reviews
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can submit reviews"
        )

    # Find booking
    booking = db.get(
        Booking,
        review_data.booking_id
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # Booking must belong to the customer
    if booking.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not the customer for this booking"
        )

    # Only completed jobs can be reviewed
    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Only completed bookings can be reviewed"
        )

    # Check if already reviewed
    existing_review = db.scalar(
        select(Review).where(
            Review.booking_id == booking.id
        )
    )

    if existing_review:
        raise HTTPException(
            status_code=400,
            detail="This booking has already been reviewed"
        )

    # Create review
    review = Review(
        booking_id=booking.id,
        customer_id=current_user.id,
        worker_id=booking.worker_id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    # ========================================================
    # RECALCULATE WORKER AVERAGE RATING
    # ========================================================

    average_rating = db.scalar(
        select(
            func.avg(Review.rating)
        ).where(
            Review.worker_id == booking.worker_id
        )
    )

    worker = db.get(
        Worker,
        booking.worker_id
    )

    if worker:
        worker.average_rating = round(
            float(average_rating or 0),
            2
        )

        db.commit()
        db.refresh(review)

    return review


# ============================================================
# CUSTOMER - VIEW MY REVIEWS
# ============================================================

@router.get(
    "/my",
    response_model=list[ReviewResponse]
)
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can view their reviews"
        )

    reviews = db.scalars(
        select(Review)
        .where(
            Review.customer_id == current_user.id
        )
        .order_by(Review.created_at.desc())
    ).all()

    return reviews


# ============================================================
# PUBLIC - VIEW WORKER REVIEWS
# ============================================================

@router.get(
    "/worker/{worker_id}",
    response_model=list[ReviewResponse]
)
def get_worker_reviews(
    worker_id: int,
    db: Session = Depends(get_db)
):
    worker = db.get(
        Worker,
        worker_id
    )

    if not worker:
        raise HTTPException(
            status_code=404,
            detail="Worker not found"
        )

    reviews = db.scalars(
        select(Review)
        .where(
            Review.worker_id == worker_id
        )
        .order_by(Review.created_at.desc())
    ).all()

    return reviews