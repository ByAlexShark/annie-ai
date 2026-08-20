from datetime import date

from app.domain.repositories.patient_repository import (
    PatientRepository,
)
from app.infrastructure.database.models.patient import Patient


class PatientNotFoundError(Exception):
    pass


class PatientAlreadyExistsError(Exception):
    pass


class PatientService:

    def __init__(
        self,
        repository: PatientRepository,
    ):
        self.repository = repository

    async def list_patients(self) -> list[Patient]:
        return await self.repository.get_all()

    async def get_patient(
        self,
        patient_id: int,
    ) -> Patient:

        patient = await self.repository.get_by_id(
            patient_id
        )

        if patient is None:
            raise PatientNotFoundError(
                "Patient not found."
            )

        return patient

    async def get_patient_by_phone(
        self,
        phone: str,
    ) -> Patient | None:
        normalized_phone = phone.strip()

        return await self.repository.get_by_phone(
            normalized_phone
        )

    async def create_patient(
        self,
        phone: str,
        first_name: str | None = None,
        last_name: str | None = None,
        document_number: str | None = None,
        birth_date: date | None = None,
    ) -> Patient:

        normalized_phone = phone.strip()

        existing = await self.repository.get_by_phone(
            normalized_phone
        )

        if existing is not None:
            raise PatientAlreadyExistsError(
                "A patient with this phone number already exists."
            )

        patient = Patient(
            phone=normalized_phone,
            first_name=(
                first_name.strip()
                if first_name
                else None
            ),
            last_name=(
                last_name.strip()
                if last_name
                else None
            ),
            document_number=document_number,
            birth_date=birth_date,
            active=True,
        )

        return await self.repository.create(
            patient
        )