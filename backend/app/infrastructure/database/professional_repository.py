from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.professional_repository import (
    ProfessionalRepository,
)
from app.infrastructure.database.models.professional import Professional


class SQLAlchemyProfessionalRepository(ProfessionalRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        care_area_id: int | None = None,
    ) -> list[Professional]:

        query = select(Professional)

        if care_area_id is not None:
            query = query.where(
                Professional.care_area_id == care_area_id
            )

        query = query.order_by(
            Professional.first_name,
            Professional.last_name,
        )

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def get_by_id(
        self,
        professional_id: int,
    ) -> Professional | None:

        return await self.session.get(
            Professional,
            professional_id,
        )

    async def create(
        self,
        professional: Professional,
    ) -> Professional:

        self.session.add(professional)

        await self.session.commit()
        await self.session.refresh(professional)

        return professional