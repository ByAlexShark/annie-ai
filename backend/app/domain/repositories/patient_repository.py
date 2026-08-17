from abc import ABC, abstractmethod

from app.infrastructure.database.models.patient import Patient


class PatientRepository(ABC):

    @abstractmethod
    async def get_all(self) -> list[Patient]:
        pass

    @abstractmethod
    async def get_by_id(
        self,
        patient_id: int,
    ) -> Patient | None:
        pass

    @abstractmethod
    async def get_by_phone(
        self,
        phone: str,
    ) -> Patient | None:
        pass

    @abstractmethod
    async def create(
        self,
        patient: Patient,
    ) -> Patient:
        pass