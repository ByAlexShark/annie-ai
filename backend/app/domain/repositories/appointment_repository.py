from abc import ABC, abstractmethod
from datetime import date

from app.infrastructure.database.models.appointment import Appointment


class AppointmentRepository(ABC):

    @abstractmethod
    async def get_all(self) -> list[Appointment]:
        pass

    @abstractmethod
    async def get_by_id(
        self,
        appointment_id: int,
    ) -> Appointment | None:
        pass

    @abstractmethod
    async def get_by_professional_and_date(
        self,
        professional_id: int,
        appointment_date: date,
    ) -> list[Appointment]:
        pass

    @abstractmethod
    async def create(
        self,
        appointment: Appointment,
    ) -> Appointment:
        pass

    @abstractmethod
    async def update(
        self,
        appointment: Appointment,
    ) -> Appointment:
        pass

    