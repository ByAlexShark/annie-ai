from abc import ABC, abstractmethod

from app.infrastructure.database.models.service import Service


class ProfessionalServiceRepository(ABC):

    @abstractmethod
    async def assign_service(
        self,
        professional_id: int,
        service_id: int,
    ) -> None:
        pass

    @abstractmethod
    async def exists(
        self,
        professional_id: int,
        service_id: int,
    ) -> bool:
        pass

    @abstractmethod
    async def get_services(
        self,
        professional_id: int,
    ) -> list[Service]:
        pass