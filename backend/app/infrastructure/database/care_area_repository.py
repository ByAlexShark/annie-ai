from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.care_area_repository import CareAreaRepository
from app.infrastructure.database.models.care_area import CareArea


class SQLAlchemyCareAreaRepository(CareAreaRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[CareArea]:
        result = await self.session.execute(
            select(CareArea).order_by(CareArea.name)
        )
        return list(result.scalars().all())

    async def get_by_id(self, area_id: int) -> CareArea | None:
        return await self.session.get(CareArea, area_id)

    async def get_by_name(self, name: str) -> CareArea | None:
        result = await self.session.execute(
            select(CareArea).where(CareArea.name == name)
        )
        return result.scalar_one_or_none()

    async def create(self, area: CareArea) -> CareArea:
        self.session.add(area)

        await self.session.commit()
        await self.session.refresh(area)

        return area
