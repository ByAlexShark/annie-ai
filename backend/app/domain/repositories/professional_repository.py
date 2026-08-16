from abc import ABC, abstractmethod

from app.infrastructure.database.models.professional import Professional


class ProfessionalRepository(ABC):

    @abstractmethod
    async def get_all(
        self,
        care_area_id: int | None = None,
    ) -> list[Professional]:
        pass

    @abstractmethod
    async def get_by_id(
        self,
        professional_id: int,
    ) -> Professional | None:
        pass

    @abstractmethod
    async def create(
        self,
        professional: Professional,
    ) -> Professional:
        pass