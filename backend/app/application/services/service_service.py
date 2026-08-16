from decimal import Decimal

from app.domain.repositories.care_area_repository import (
    CareAreaRepository,
)
from app.domain.repositories.service_repository import (
    ServiceRepository,
)
from app.infrastructure.database.models.service import Service


class ServiceNotFoundError(Exception):
    pass


class ServiceAlreadyExistsError(Exception):
    pass


class InvalidCareAreaError(Exception):
    pass


class ServiceService:

    def __init__(
        self,
        service_repository: ServiceRepository,
        care_area_repository: CareAreaRepository,
    ):
        self.service_repository = service_repository
        self.care_area_repository = care_area_repository

    async def list_services(
        self,
        area_id: int | None = None,
    ) -> list[Service]:

        if area_id is not None:

            area = await self.care_area_repository.get_by_id(
                area_id
            )

            if area is None:
                raise InvalidCareAreaError(
                    f"Care area with id {area_id} was not found."
                )

        return await self.service_repository.get_all(
            area_id=area_id
        )

    async def get_service(
        self,
        service_id: int,
    ) -> Service:

        service = await self.service_repository.get_by_id(
            service_id
        )

        if service is None:
            raise ServiceNotFoundError(
                f"Service with id {service_id} was not found."
            )

        return service

    async def create_service(
        self,
        area_id: int,
        name: str,
        description: str | None = None,
        default_duration_minutes: int = 30,
        price: Decimal | None = None,
        currency: str = "BOB",
    ) -> Service:

        area = await self.care_area_repository.get_by_id(
            area_id
        )

        if area is None:
            raise InvalidCareAreaError(
                f"Care area with id {area_id} was not found."
            )

        normalized_name = name.strip()

        existing = await self.service_repository.get_by_name(
            area_id=area_id,
            name=normalized_name,
        )

        if existing is not None:
            raise ServiceAlreadyExistsError(
                f"Service '{normalized_name}' already exists "
                f"in care area '{area.name}'."
            )

        service = Service(
            area_id=area_id,
            name=normalized_name,
            description=description,
            default_duration_minutes=default_duration_minutes,
            price=price,
            currency=currency.upper(),
            active=True,
        )

        return await self.service_repository.create(service)