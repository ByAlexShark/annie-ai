from abc import ABC, abstractmethod

from app.infrastructure.database.models.professional_schedule import (
    ProfessionalSchedule,
)


class ScheduleRepository(ABC):

    @abstractmethod
    async def get_by_professional(
        self,
        professional_id: int,
    ) -> list[ProfessionalSchedule]:
        pass

    @abstractmethod
    async def get_by_professional_and_day(
        self,
        professional_id: int,
        day_of_week: int,
    ) -> list[ProfessionalSchedule]:
        pass

    @abstractmethod
    async def create(
        self,
        schedule: ProfessionalSchedule,
    ) -> ProfessionalSchedule:
        pass