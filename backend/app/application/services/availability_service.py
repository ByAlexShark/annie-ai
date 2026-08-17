from datetime import date, datetime, timedelta

from app.domain.repositories.appointment_repository import (
    AppointmentRepository,
)
from app.domain.repositories.professional_repository import (
    ProfessionalRepository,
)
from app.domain.repositories.professional_service_repository import (
    ProfessionalServiceRepository,
)
from app.domain.repositories.schedule_repository import (
    ScheduleRepository,
)


class AvailabilityProfessionalNotFoundError(Exception):
    pass


class AvailabilityServiceNotAssignedError(Exception):
    pass


class AvailabilityService:

    def __init__(
        self,
        professional_repository: ProfessionalRepository,
        schedule_repository: ScheduleRepository,
        appointment_repository: AppointmentRepository,
        professional_service_repository: ProfessionalServiceRepository,
    ):
        self.professional_repository = professional_repository
        self.schedule_repository = schedule_repository
        self.appointment_repository = appointment_repository
        self.professional_service_repository = (
            professional_service_repository
        )

    async def get_available_slots(
        self,
        professional_id: int,
        service_id: int,
        requested_date: date,
    ) -> list[str]:

        professional = (
            await self.professional_repository.get_by_id(
                professional_id
            )
        )

        if professional is None:
            raise AvailabilityProfessionalNotFoundError(
                "Professional not found."
            )

        service_assigned = (
            await self.professional_service_repository.exists(
                professional_id=professional_id,
                service_id=service_id,
            )
        )

        if not service_assigned:
            raise AvailabilityServiceNotAssignedError(
                "The professional does not provide this service."
            )

        day_of_week = requested_date.weekday()

        schedules = (
            await self.schedule_repository.get_by_professional_and_day(
                professional_id=professional_id,
                day_of_week=day_of_week,
            )
        )

        if not schedules:
            return []

        appointments = (
            await self.appointment_repository.get_by_professional_and_date(
                professional_id=professional_id,
                appointment_date=requested_date,
            )
        )

        occupied_times = {
            appointment.start_time
            for appointment in appointments
        }

        available_slots: list[str] = []

        for schedule in schedules:

            current = datetime.combine(
                requested_date,
                schedule.start_time,
            )

            schedule_end = datetime.combine(
                requested_date,
                schedule.end_time,
            )

            duration = timedelta(
                minutes=schedule.appointment_duration_minutes
            )

            generated_slots = 0

            while current + duration <= schedule_end:

                if (
                    schedule.max_appointments is not None
                    and generated_slots >= schedule.max_appointments
                ):
                    break

                slot_time = current.time()

                if slot_time not in occupied_times:
                    available_slots.append(
                        slot_time.strftime("%H:%M")
                    )

                current += duration
                generated_slots += 1

        return available_slots