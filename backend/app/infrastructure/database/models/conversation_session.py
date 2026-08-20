from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, TimestampMixin


class ConversationSession(TimestampMixin, Base):
    __tablename__ = "conversation_sessions"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    phone: Mapped[str] = mapped_column(
        String(25),
        unique=True,
        index=True,
        nullable=False,
    )

    state: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="idle",
        server_default="idle",
    )

    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "patients.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    service_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "services.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    professional_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "professionals.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    requested_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )