from __future__ import annotations

from datetime import date, time

from sqlalchemy import (
    Date,
    Enum,
    ForeignKey,
    String,
    Text,
    Time,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums.appointment_status import AppointmentStatus
from app.infrastructure.database.base import Base, TimestampMixin


class Appointment(TimestampMixin, Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)

    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        nullable=False,
        index=True,
    )

    professional_id: Mapped[int] = mapped_column(
        ForeignKey("professionals.id"),
        nullable=False,
        index=True,
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id"),
        nullable=False,
        index=True,
    )

    appointment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False,
    )

    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(
            AppointmentStatus,
            name="appointment_status",
        ),
        nullable=False,
        default=AppointmentStatus.PENDING,
    )

    source: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="whatsapp",
        server_default="whatsapp",
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    patient: Mapped["Patient"] = relationship()

    professional: Mapped["Professional"] = relationship(
        back_populates="appointments",
    )

    service: Mapped["Service"] = relationship()
