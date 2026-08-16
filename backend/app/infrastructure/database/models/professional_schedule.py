from __future__ import annotations

from datetime import time

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Integer,
    Time,
    UniqueConstraint,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin


class ProfessionalSchedule(TimestampMixin, Base):
    __tablename__ = "professional_schedules"

    __table_args__ = (
        CheckConstraint(
            "day_of_week >= 0 AND day_of_week <= 6",
            name="valid_day_of_week",
        ),
        CheckConstraint(
            "start_time < end_time",
            name="valid_schedule_time_range",
        ),
        UniqueConstraint(
            "professional_id",
            "day_of_week",
            "start_time",
            "end_time",
            name="uq_professional_schedule",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    professional_id: Mapped[int] = mapped_column(
        ForeignKey("professionals.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 0 = lunes, 6 = domingo
    day_of_week: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    appointment_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
        server_default="30",
    )

    max_appointments: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    professional: Mapped["Professional"] = relationship(
        back_populates="schedules",
    )
