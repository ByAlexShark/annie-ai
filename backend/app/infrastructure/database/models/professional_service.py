from __future__ import annotations

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin


class ProfessionalService(TimestampMixin, Base):
    __tablename__ = "professional_services"

    __table_args__ = (
        UniqueConstraint(
            "professional_id",
            "service_id",
            name="uq_professional_service",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    professional_id: Mapped[int] = mapped_column(
        ForeignKey(
            "professionals.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    service_id: Mapped[int] = mapped_column(
        ForeignKey(
            "services.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    professional: Mapped["Professional"] = relationship(
        back_populates="professional_services",
    )

    service: Mapped["Service"] = relationship(
        back_populates="professional_services",
    )