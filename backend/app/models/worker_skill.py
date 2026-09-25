from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SkillLevel(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class WorkerSkill(Base):
    __tablename__ = "worker_skills"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"),
        nullable=False
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id"),
        nullable=False
    )

    skill_level: Mapped[SkillLevel] = mapped_column(
        SQLEnum(SkillLevel),
        default=SkillLevel.BEGINNER,
        nullable=False
    )

    years_experience: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )