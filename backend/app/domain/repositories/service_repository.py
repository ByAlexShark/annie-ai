from abc import ABC, abstractmethod

from app.infrastructure.database.models.service import Service


class ServiceRepository(ABC):

    @abstractmethod
    async def get_all(
        self,
        area_id: int | None = None,
    ) -> list[Service]:
        pass

    @abstractmethod
    async def get_by_id(
        self,
        service_id: int,
    ) -> Service | None:
        pass

    @abstractmethod
    async def get_by_name(
        self,
        area_id: int,
        name: str,
    ) -> Service | None:
        pass

    @abstractmethod
    async def create(
        self,
        service: Service,
    ) -> Service:
        pass