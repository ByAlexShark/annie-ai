from abc import ABC, abstractmethod

from app.infrastructure.database.models.care_area import CareArea


class CareAreaRepository(ABC):

    @abstractmethod
    async def get_all(self) -> list[CareArea]:
        pass

    @abstractmethod
    async def get_by_id(self, area_id: int) -> CareArea | None:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> CareArea | None:
        pass

    @abstractmethod
    async def create(self, area: CareArea) -> CareArea:
        pass
