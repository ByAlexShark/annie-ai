from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin


class Professional(TimestampMixin, Base):
    __tablename__ = "professionals"

    id: Mapped[int] = mapped_column(primary_key=True)

    care_area_id: Mapped[int] = mapped_column(
        ForeignKey("care_areas.id"),
        nullable=False,
        index=True,
    )

    first_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    last_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    license_number: Mapped[str | None] = mapped_column(
        String(50),
        unique=True,
        nullable=True,
    )

    phone: Mapped[str | None] = mapped_column(
        String(25),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    schedules: Mapped[list["ProfessionalSchedule"]] = relationship(
        back_populates="professional",
        cascade="all, delete-orphan",
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="professional",
    )

    professional_services: Mapped[list["ProfessionalService"]] = relationship(
    back_populates="professional",
    cascade="all, delete-orphan",
)
