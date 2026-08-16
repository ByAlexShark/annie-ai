from __future__ import annotations

from sqlalchemy import Boolean, String, Text, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base, TimestampMixin


class CareArea(TimestampMixin, Base):
    __tablename__ = "care_areas"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=true(),
    )

    services: Mapped[list["Service"]] = relationship(
        back_populates="area",
        cascade="all, delete-orphan",
    )
