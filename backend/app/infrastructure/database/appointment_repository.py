from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.enums.appointment_status import AppointmentStatus
from app.domain.repositories.appointment_repository import (
    AppointmentRepository,
)
from app.infrastructure.database.models.appointment import Appointment


class SQLAlchemyAppointmentRepository(
    AppointmentRepository
):

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_all(self) -> list[Appointment]:

        result = await self.session.execute(
            select(Appointment).order_by(
                Appointment.appointment_date,
                Appointment.start_time,
            )
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        appointment_id: int,
    ) -> Appointment | None:

        return await self.session.get(
            Appointment,
            appointment_id,
        )

    async def get_by_professional_and_date(
        self,
        professional_id: int,
        appointment_date: date,
    ) -> list[Appointment]:

        result = await self.session.execute(
            select(Appointment).where(
                Appointment.professional_id
                == professional_id,

                Appointment.appointment_date
                == appointment_date,

                Appointment.status.in_(
                    [
                        AppointmentStatus.PENDING,
                        AppointmentStatus.CONFIRMED,
                    ]
                ),
            )
        )

        return list(result.scalars().all())

    async def create(
        self,
        appointment: Appointment,
    ) -> Appointment:

        self.session.add(appointment)

        await self.session.commit()
        await self.session.refresh(appointment)

        return appointment