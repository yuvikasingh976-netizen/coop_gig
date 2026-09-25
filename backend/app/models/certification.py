from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Certification(Base):
    __tablename__ = "certifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    issuing_organization: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    certificate_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    issue_date: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    expiry_date: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    is_verified: Mapped[bool] = mapped_column(
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )