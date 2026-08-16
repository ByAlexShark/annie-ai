from __future__ import annotations

from decimal import Decimal

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin


class Service(TimestampMixin, Base):
    __tablename__ = "services"

    __table_args__ = (
        UniqueConstraint(
            "area_id",
            "name",
            name="uq_services_area_name",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    area_id: Mapped[int] = mapped_column(
        ForeignKey("care_areas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    default_duration_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
        server_default="30",
    )

    # Lo dejamos preparado para cuando el hospital nos dé los precios.
    price: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="BOB",
        server_default="BOB",
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    area: Mapped["CareArea"] = relationship(
        back_populates="services",
    )

    professional_services: Mapped[list["ProfessionalService"]] = relationship(
    back_populates="service",
    cascade="all, delete-orphan",
)
