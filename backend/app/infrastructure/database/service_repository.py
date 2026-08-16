from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.service_repository import ServiceRepository
from app.infrastructure.database.models.service import Service


class SQLAlchemyServiceRepository(ServiceRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        area_id: int | None = None,
    ) -> list[Service]:

        query = select(Service)

        if area_id is not None:
            query = query.where(Service.area_id == area_id)

        query = query.order_by(Service.name)

        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def get_by_id(
        self,
        service_id: int,
    ) -> Service | None:

        return await self.session.get(
            Service,
            service_id,
        )

    async def get_by_name(
        self,
        area_id: int,
        name: str,
    ) -> Service | None:

        result = await self.session.execute(
            select(Service).where(
                Service.area_id == area_id,
                Service.name == name,
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        service: Service,
    ) -> Service:

        self.session.add(service)

        await self.session.commit()
        await self.session.refresh(service)

        return service