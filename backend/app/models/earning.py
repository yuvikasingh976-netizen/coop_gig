from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkerEarning(Base):
    __tablename__ = "worker_earnings"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"),
        nullable=False
    )

    payment_id: Mapped[int] = mapped_column(
        ForeignKey("payments.id"),
        unique=True,
        nullable=False
    )

    amount: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    earning_type: Mapped[str] = mapped_column(
        String(50),
        default="JOB_PAYMENT",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )