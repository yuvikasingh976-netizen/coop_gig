from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user

from app.models.user import User, UserRole
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.worker import Worker
from app.models.invoice import Invoice
from app.models.earning import WorkerEarning

from app.schemas.payment import (
    PaymentCreate,
    PaymentResponse
)

from app.schemas.invoice import InvoiceResponse
from app.schemas.earning import EarningResponse


router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


# ============================================================
# CUSTOMER - CREATE PAYMENT
# ============================================================

@router.post(
    "/",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can make payments"
        )

    booking = db.get(
        Booking,
        payment_data.booking_id
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not the customer for this booking"
        )

    if booking.status != BookingStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Payment can only be made for completed bookings"
        )

    existing_payment = db.scalar(
        select(Payment).where(
            Payment.booking_id == booking.id
        )
    )

    if existing_payment:
        raise HTTPException(
            status_code=400,
            detail="Payment already exists for this booking"
        )

    transaction_id = (
        "TXN-" + uuid4().hex[:12].upper()
    )

    payment = Payment(
        booking_id=booking.id,
        customer_id=booking.customer_id,
        worker_id=booking.worker_id,
        amount=booking.estimated_amount,
        payment_method=payment_data.payment_method,
        status=PaymentStatus.PENDING,
        transaction_id=transaction_id
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


# ============================================================
# CUSTOMER - MARK PAYMENT SUCCESS
# ============================================================

@router.patch(
    "/{payment_id}/success",
    response_model=PaymentResponse
)
def mark_payment_success(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can update payments"
        )

    payment = db.get(
        Payment,
        payment_id
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    if payment.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to update this payment"
        )

    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending payments can be marked successful"
        )

    payment.status = PaymentStatus.SUCCESS

    # ========================================================
    # CREATE INVOICE
    # ========================================================

    existing_invoice = db.scalar(
        select(Invoice).where(
            Invoice.payment_id == payment.id
        )
    )

    if not existing_invoice:

        invoice_number = (
            "INV-" + uuid4().hex[:8].upper()
        )

        invoice = Invoice(
            invoice_number=invoice_number,
            payment_id=payment.id,
            booking_id=payment.booking_id,
            customer_id=payment.customer_id,
            worker_id=payment.worker_id,
            amount=payment.amount,
            status="PAID"
        )

        db.add(invoice)

    # ========================================================
    # CREATE WORKER EARNING
    # ========================================================

    existing_earning = db.scalar(
        select(WorkerEarning).where(
            WorkerEarning.payment_id == payment.id
        )
    )

    if not existing_earning:

        earning = WorkerEarning(
            worker_id=payment.worker_id,
            payment_id=payment.id,
            amount=payment.amount,
            earning_type="JOB_PAYMENT"
        )

        db.add(earning)

    db.commit()
    db.refresh(payment)

    return payment


# ============================================================
# CUSTOMER - VIEW MY PAYMENTS
# ============================================================

@router.get(
    "/my",
    response_model=list[PaymentResponse]
)
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can view their payments"
        )

    payments = db.scalars(
        select(Payment)
        .where(
            Payment.customer_id == current_user.id
        )
        .order_by(Payment.created_at.desc())
    ).all()

    return payments


# ============================================================
# WORKER - VIEW SUCCESSFUL PAYMENTS
# ============================================================

@router.get(
    "/worker",
    response_model=list[PaymentResponse]
)
def get_worker_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can view worker payments"
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

    payments = db.scalars(
        select(Payment)
        .where(
            Payment.worker_id == worker.id,
            Payment.status == PaymentStatus.SUCCESS
        )
        .order_by(Payment.created_at.desc())
    ).all()

    return payments


# ============================================================
# CUSTOMER - VIEW MY INVOICES
# ============================================================

@router.get(
    "/invoices",
    response_model=list[InvoiceResponse]
)
def get_my_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(
            status_code=403,
            detail="Only customers can view their invoices"
        )

    invoices = db.scalars(
        select(Invoice)
        .where(
            Invoice.customer_id == current_user.id
        )
        .order_by(Invoice.issued_at.desc())
    ).all()

    return invoices


# ============================================================
# WORKER - VIEW MY INVOICES
# ============================================================

@router.get(
    "/worker/invoices",
    response_model=list[InvoiceResponse]
)
def get_worker_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can view their invoices"
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

    invoices = db.scalars(
        select(Invoice)
        .where(
            Invoice.worker_id == worker.id
        )
        .order_by(Invoice.issued_at.desc())
    ).all()

    return invoices


# ============================================================
# WORKER - VIEW EARNINGS
# ============================================================

@router.get(
    "/worker/earnings",
    response_model=list[EarningResponse]
)
def get_worker_earnings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can view earnings"
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

    earnings = db.scalars(
        select(WorkerEarning)
        .where(
            WorkerEarning.worker_id == worker.id
        )
        .order_by(WorkerEarning.created_at.desc())
    ).all()

    return earnings


# ============================================================
# WORKER - EARNINGS SUMMARY
# ============================================================

@router.get(
    "/worker/earnings/summary"
)
def get_worker_earnings_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != UserRole.WORKER:
        raise HTTPException(
            status_code=403,
            detail="Only workers can view earnings summary"
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

    total_earnings = db.scalar(
        select(
            func.coalesce(
                func.sum(WorkerEarning.amount),
                0
            )
        ).where(
            WorkerEarning.worker_id == worker.id
        )
    )

    total_jobs = db.scalar(
        select(
            func.count(WorkerEarning.id)
        ).where(
            WorkerEarning.worker_id == worker.id
        )
    )

    return {
        "worker_id": worker.id,
        "total_earnings": float(total_earnings or 0),
        "total_jobs": int(total_jobs or 0)
    }