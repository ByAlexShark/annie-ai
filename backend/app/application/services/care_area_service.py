from app.domain.repositories.care_area_repository import CareAreaRepository
from app.infrastructure.database.models.care_area import CareArea


class CareAreaAlreadyExistsError(Exception):
    pass


class CareAreaNotFoundError(Exception):
    pass


class CareAreaService:

    def __init__(self, repository: CareAreaRepository):
        self.repository = repository

    async def list_areas(self) -> list[CareArea]:
        return await self.repository.get_all()

    async def get_area(self, area_id: int) -> CareArea:
        area = await self.repository.get_by_id(area_id)

        if area is None:
            raise CareAreaNotFoundError(
                f"Care area with id {area_id} was not found."
            )

        return area

    async def create_area(
        self,
        name: str,
        description: str | None = None,
    ) -> CareArea:

        normalized_name = name.strip()

        existing_area = await self.repository.get_by_name(
            normalized_name
        )

        if existing_area is not None:
            raise CareAreaAlreadyExistsError(
                f"Care area '{normalized_name}' already exists."
            )

        area = CareArea(
            name=normalized_name,
            description=description,
            active=True,
        )

        return await self.repository.create(area)
