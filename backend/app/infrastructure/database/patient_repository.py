from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.patient_repository import (
    PatientRepository,
)
from app.infrastructure.database.models.patient import Patient


class SQLAlchemyPatientRepository(PatientRepository):

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_all(self) -> list[Patient]:

        result = await self.session.execute(
            select(Patient).order_by(
                Patient.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def get_by_id(
        self,
        patient_id: int,
    ) -> Patient | None:

        return await self.session.get(
            Patient,
            patient_id,
        )

    async def get_by_phone(
        self,
        phone: str,
    ) -> Patient | None:

        result = await self.session.execute(
            select(Patient).where(
                Patient.phone == phone
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        patient: Patient,
    ) -> Patient:

        self.session.add(patient)

        await self.session.commit()
        await self.session.refresh(patient)

        return patient