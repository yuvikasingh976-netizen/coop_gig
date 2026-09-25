from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, UserRole
from app.models.payment import Payment, PaymentStatus


router = APIRouter(
    prefix="/admin/payments",
    tags=["Admin - Payments"]
)


# ---------------------------------------------------------
# VIEW ALL PAYMENTS
# ---------------------------------------------------------

@router.get("/")
def get_all_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    payments = db.scalars(
        select(Payment).order_by(
            Payment.created_at.desc()
        )
    ).all()

    result = []

    for payment in payments:

        customer = db.scalar(
            select(User).where(
                User.id == payment.customer_id
            )
        )

        result.append({
            "payment_id": payment.id,
            "booking_id": payment.booking_id,
            "customer_id": payment.customer_id,
            "customer_name": (
                customer.name
                if customer
                else None
            ),
            "worker_id": payment.worker_id,
            "amount": payment.amount,
            "payment_method": payment.payment_method.value,
            "status": payment.status.value,
            "transaction_id": payment.transaction_id,
            "created_at": payment.created_at
        })

    return result


# ---------------------------------------------------------
# REVENUE SUMMARY
# ---------------------------------------------------------

@router.get("/summary")
def get_payment_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    total_payments = db.scalar(
        select(func.count(Payment.id))
    ) or 0

    successful_payments = db.scalar(
        select(func.count(Payment.id)).where(
            Payment.status == PaymentStatus.SUCCESS
        )
    ) or 0

    pending_payments = db.scalar(
        select(func.count(Payment.id)).where(
            Payment.status == PaymentStatus.PENDING
        )
    ) or 0

    failed_payments = db.scalar(
        select(func.count(Payment.id)).where(
            Payment.status == PaymentStatus.FAILED
        )
    ) or 0

    total_revenue = db.scalar(
        select(
            func.coalesce(
                func.sum(Payment.amount),
                0
            )
        ).where(
            Payment.status == PaymentStatus.SUCCESS
        )
    ) or 0

    return {
        "total_payments": total_payments,
        "successful_payments": successful_payments,
        "pending_payments": pending_payments,
        "failed_payments": failed_payments,
        "total_revenue": float(total_revenue)
    }