from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class WorkerWelfare(Base):
    __tablename__ = "worker_welfare"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"),
        unique=True,
        nullable=False
    )

    insurance_provider: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    policy_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    coverage_amount: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )

    welfare_contribution: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )

    emergency_support: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )