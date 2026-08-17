from datetime import date, datetime, time, timedelta

from app.application.services.availability_service import (
    AvailabilityService,
)
from app.domain.enums.appointment_status import (
    AppointmentStatus,
)
from app.domain.repositories.appointment_repository import (
    AppointmentRepository,
)
from app.domain.repositories.patient_repository import (
    PatientRepository,
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
from app.domain.repositories.service_repository import (
    ServiceRepository,
)
from app.infrastructure.database.models.appointment import (
    Appointment,
)


class AppointmentNotFoundError(Exception):
    pass


class AppointmentPatientNotFoundError(Exception):
    pass


class AppointmentProfessionalNotFoundError(Exception):
    pass


class AppointmentServiceNotFoundError(Exception):
    pass


class AppointmentServiceNotAssignedError(Exception):
    pass


class AppointmentSlotUnavailableError(Exception):
    pass


class AppointmentInvalidScheduleError(Exception):
    pass

class AppointmentInvalidStatusError(Exception):
    pass

class AppointmentRescheduleError(Exception):
    pass


class AppointmentService:

    def __init__(
        self,
        appointment_repository: AppointmentRepository,
        patient_repository: PatientRepository,
        professional_repository: ProfessionalRepository,
        service_repository: ServiceRepository,
        professional_service_repository: ProfessionalServiceRepository,
        schedule_repository: ScheduleRepository,
        availability_service: AvailabilityService,
    ):
        self.appointment_repository = appointment_repository
        self.patient_repository = patient_repository
        self.professional_repository = professional_repository
        self.service_repository = service_repository
        self.professional_service_repository = (
            professional_service_repository
        )
        self.schedule_repository = schedule_repository
        self.availability_service = availability_service

    async def list_appointments(
        self,
    ) -> list[Appointment]:

        return await self.appointment_repository.get_all()

    async def get_appointment(
        self,
        appointment_id: int,
    ) -> Appointment:

        appointment = (
            await self.appointment_repository.get_by_id(
                appointment_id
            )
        )

        if appointment is None:
            raise AppointmentNotFoundError(
                "Appointment not found."
            )

        return appointment

    async def create_appointment(
        self,
        patient_id: int,
        professional_id: int,
        service_id: int,
        appointment_date: date,
        start_time: time,
        reason: str | None = None,
        source: str = "whatsapp",
    ) -> Appointment:

        patient = await self.patient_repository.get_by_id(
            patient_id
        )

        if patient is None:
            raise AppointmentPatientNotFoundError(
                "Patient not found."
            )

        professional = (
            await self.professional_repository.get_by_id(
                professional_id
            )
        )

        if professional is None:
            raise AppointmentProfessionalNotFoundError(
                "Professional not found."
            )

        service = await self.service_repository.get_by_id(
            service_id
        )

        if service is None:
            raise AppointmentServiceNotFoundError(
                "Service not found."
            )

        service_assigned = (
            await self.professional_service_repository.exists(
                professional_id=professional_id,
                service_id=service_id,
            )
        )

        if not service_assigned:
            raise AppointmentServiceNotAssignedError(
                "The professional does not provide this service."
            )

        available_slots = (
            await self.availability_service.get_available_slots(
                professional_id=professional_id,
                service_id=service_id,
                requested_date=appointment_date,
            )
        )

        requested_slot = start_time.strftime("%H:%M")

        if requested_slot not in available_slots:
            raise AppointmentSlotUnavailableError(
                "The requested appointment slot is not available."
            )

        end_time = await self._calculate_end_time(
            professional_id=professional_id,
            appointment_date=appointment_date,
            start_time=start_time,
        )

        appointment = Appointment(
            patient_id=patient_id,
            professional_id=professional_id,
            service_id=service_id,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            status=AppointmentStatus.CONFIRMED,
            source=source,
            reason=reason,
        )

        return await self.appointment_repository.create(
            appointment
        )

    async def cancel_appointment(
        self,
        appointment_id: int,
    ) -> Appointment:

        appointment = (
            await self.appointment_repository.get_by_id(
                appointment_id
            )
        )

        if appointment is None:
            raise AppointmentNotFoundError(
                "Appointment not found."
            )

        if appointment.status not in (
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
        ):
            raise AppointmentInvalidStatusError(
                "Only pending or confirmed appointments can be cancelled."
            )

        appointment.status = AppointmentStatus.CANCELLED

        return await self.appointment_repository.update(
            appointment
        ) 
    async def reschedule_appointment(
        self,
        appointment_id: int,
        appointment_date: date,
        start_time: time,
    ) -> Appointment:

        appointment = (
            await self.appointment_repository.get_by_id(
                appointment_id
            )
        )

        if appointment is None:
            raise AppointmentNotFoundError(
                "Appointment not found."
            )

        if appointment.status not in (
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
        ):
            raise AppointmentInvalidStatusError(
                "Only pending or confirmed appointments "
                "can be rescheduled."
            )

        available_slots = (
            await self.availability_service.get_available_slots(
                professional_id=appointment.professional_id,
                service_id=appointment.service_id,
                requested_date=appointment_date,
            )
        )
        requested_slot = start_time.strftime("%H:%M")

        if requested_slot not in available_slots:
            raise AppointmentSlotUnavailableError(
                "The requested appointment slot is not available."
            )

        end_time = await self._calculate_end_time(
            professional_id=appointment.professional_id,
            appointment_date=appointment_date,
            start_time=start_time,
        )

        appointment.appointment_date = appointment_date
        appointment.start_time = start_time
        appointment.end_time = end_time

        return await self.appointment_repository.update(
            appointment
        )

    async def _calculate_end_time(
        self,
        professional_id: int,
        appointment_date: date,
        start_time: time,
    ) -> time:

        schedules = (
            await self.schedule_repository.get_by_professional_and_day(
                professional_id=professional_id,
                day_of_week=appointment_date.weekday(),
            )
        )

        requested_start = datetime.combine(
            appointment_date,
            start_time,
        )

        for schedule in schedules:

            schedule_start = datetime.combine(
                appointment_date,
                schedule.start_time,
            )

            schedule_end = datetime.combine(
                appointment_date,
                schedule.end_time,
            )

            duration = timedelta(
                minutes=schedule.appointment_duration_minutes
            )

            current = schedule_start

            while current + duration <= schedule_end:

                if current == requested_start:
                    return (
                        current + duration
                    ).time()

                current += duration

        raise AppointmentInvalidScheduleError(
            "The requested time does not match "
            "a valid professional schedule."
        )