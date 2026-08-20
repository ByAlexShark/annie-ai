from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.professional_service_repository import (
    ProfessionalServiceRepository,
)
from app.infrastructure.database.models.professional_service import (
    ProfessionalService,
)
from app.infrastructure.database.models.service import Service


class SQLAlchemyProfessionalServiceRepository(
    ProfessionalServiceRepository
):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def assign_service(
        self,
        professional_id: int,
        service_id: int,
    ) -> None:

        relation = ProfessionalService(
            professional_id=professional_id,
            service_id=service_id,
        )

        self.session.add(relation)
        await self.session.commit()

    async def exists(
        self,
        professional_id: int,
        service_id: int,
    ) -> bool:

        result = await self.session.execute(
            select(ProfessionalService).where(
                ProfessionalService.professional_id == professional_id,
                ProfessionalService.service_id == service_id,
            )
        )

        return result.scalar_one_or_none() is not None

    async def get_services(
        self,
        professional_id: int,
    ) -> list[Service]:

        result = await self.session.execute(
            select(Service)
            .join(
                ProfessionalService,
                ProfessionalService.service_id == Service.id,
            )
            .where(
                ProfessionalService.professional_id == professional_id
            )
            .order_by(Service.name)
        )

        return list(result.scalars().all())

    async def get_professional_ids_by_service(
        self,
        service_id: int,
    ) -> list[int]:
        result = await self.session.execute(
            select(
                ProfessionalService.professional_id
            )
            .where(
                ProfessionalService.service_id == service_id
            )
            .order_by(
                ProfessionalService.professional_id
            )
        )

        return list(result.scalars().all())