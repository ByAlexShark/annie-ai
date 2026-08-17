from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.schedule_repository import ScheduleRepository
from app.infrastructure.database.models.professional_schedule import (
    ProfessionalSchedule,
)


class SQLAlchemyScheduleRepository(ScheduleRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_professional(
        self,
        professional_id: int,
    ) -> list[ProfessionalSchedule]:

        result = await self.session.execute(
            select(ProfessionalSchedule)
            .where(
                ProfessionalSchedule.professional_id
                == professional_id
            )
            .order_by(
                ProfessionalSchedule.day_of_week,
                ProfessionalSchedule.start_time,
            )
        )

        return list(result.scalars().all())

    async def get_by_professional_and_day(
        self,
        professional_id: int,
        day_of_week: int,
    ) -> list[ProfessionalSchedule]:

        result = await self.session.execute(
            select(ProfessionalSchedule)
            .where(
                ProfessionalSchedule.professional_id
                == professional_id,
                ProfessionalSchedule.day_of_week
                == day_of_week,
                ProfessionalSchedule.active.is_(True),
            )
            .order_by(
                ProfessionalSchedule.start_time
            )
        )

        return list(result.scalars().all())

    async def create(
        self,
        schedule: ProfessionalSchedule,
    ) -> ProfessionalSchedule:

        self.session.add(schedule)

        await self.session.commit()
        await self.session.refresh(schedule)

        return schedule