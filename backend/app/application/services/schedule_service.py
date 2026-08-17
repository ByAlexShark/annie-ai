from datetime import time

from app.domain.repositories.professional_repository import (
    ProfessionalRepository,
)
from app.domain.repositories.schedule_repository import (
    ScheduleRepository,
)
from app.infrastructure.database.models.professional_schedule import (
    ProfessionalSchedule,
)


class ScheduleProfessionalNotFoundError(Exception):
    pass


class InvalidScheduleError(Exception):
    pass


class ScheduleService:

    HOSPITAL_OPENING_TIME = time(8, 0)
    HOSPITAL_CLOSING_TIME = time(21, 0)

    def __init__(
        self,
        schedule_repository: ScheduleRepository,
        professional_repository: ProfessionalRepository,
    ):
        self.schedule_repository = schedule_repository
        self.professional_repository = professional_repository

    async def list_schedules(
        self,
        professional_id: int,
    ) -> list[ProfessionalSchedule]:

        professional = (
            await self.professional_repository.get_by_id(
                professional_id
            )
        )

        if professional is None:
            raise ScheduleProfessionalNotFoundError(
                "Professional not found."
            )

        return await self.schedule_repository.get_by_professional(
            professional_id
        )

    async def create_schedule(
        self,
        professional_id: int,
        day_of_week: int,
        start_time: time,
        end_time: time,
        appointment_duration_minutes: int = 30,
        max_appointments: int | None = None,
    ) -> ProfessionalSchedule:

        professional = (
            await self.professional_repository.get_by_id(
                professional_id
            )
        )

        if professional is None:
            raise ScheduleProfessionalNotFoundError(
                "Professional not found."
            )

        if start_time >= end_time:
            raise InvalidScheduleError(
                "Start time must be before end time."
            )

        if (
            start_time < self.HOSPITAL_OPENING_TIME
            or end_time > self.HOSPITAL_CLOSING_TIME
        ):
            raise InvalidScheduleError(
                "Schedule must be inside hospital hours "
                "08:00 - 21:00."
            )

        schedule = ProfessionalSchedule(
            professional_id=professional_id,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            appointment_duration_minutes=(
                appointment_duration_minutes
            ),
            max_appointments=max_appointments,
            active=True,
        )

        return await self.schedule_repository.create(
            schedule
        )