from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, UserRole
from app.models.review import Review
from app.models.worker import Worker


router = APIRouter(
    prefix="/admin/reviews",
    tags=["Admin - Reviews"]
)


# ---------------------------------------------------------
# VIEW ALL REVIEWS
# ---------------------------------------------------------

@router.get("/")
def get_all_reviews(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    reviews = db.scalars(
        select(Review).order_by(
            Review.created_at.desc()
        )
    ).all()

    result = []

    for review in reviews:

        customer = db.scalar(
            select(User).where(
                User.id == review.customer_id
            )
        )

        worker = db.scalar(
            select(Worker).where(
                Worker.id == review.worker_id
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
            "review_id": review.id,
            "booking_id": review.booking_id,

            "customer_id": review.customer_id,
            "customer_name": (
                customer.name
                if customer
                else None
            ),

            "worker_id": review.worker_id,
            "worker_name": (
                worker_user.name
                if worker_user
                else None
            ),

            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at
        })

    return result


# ---------------------------------------------------------
# REVIEW SUMMARY
# ---------------------------------------------------------

@router.get("/summary")
def get_review_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    total_reviews = len(
        db.scalars(
            select(Review)
        ).all()
    )

    average_rating = db.scalar(
        select(
            __import__(
                "sqlalchemy",
                fromlist=["func"]
            ).func.avg(Review.rating)
        )
    )

    five_star = len(
        db.scalars(
            select(Review).where(
                Review.rating == 5
            )
        ).all()
    )

    four_star = len(
        db.scalars(
            select(Review).where(
                Review.rating == 4
            )
        ).all()
    )

    three_star = len(
        db.scalars(
            select(Review).where(
                Review.rating == 3
            )
        ).all()
    )

    two_star = len(
        db.scalars(
            select(Review).where(
                Review.rating == 2
            )
        ).all()
    )

    one_star = len(
        db.scalars(
            select(Review).where(
                Review.rating == 1
            )
        ).all()
    )

    return {
        "total_reviews": total_reviews,
        "average_rating": (
            round(float(average_rating), 2)
            if average_rating is not None
            else 0.0
        ),
        "rating_distribution": {
            "5": five_star,
            "4": four_star,
            "3": three_star,
            "2": two_star,
            "1": one_star
        }
    }