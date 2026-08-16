from app.domain.repositories.professional_repository import (
    ProfessionalRepository,
)
from app.domain.repositories.professional_service_repository import (
    ProfessionalServiceRepository,
)
from app.domain.repositories.service_repository import (
    ServiceRepository,
)
from app.infrastructure.database.models.service import Service


class AssignmentProfessionalNotFoundError(Exception):
    pass


class AssignmentServiceNotFoundError(Exception):
    pass


class ServiceAlreadyAssignedError(Exception):
    pass


class ServiceDoesNotBelongToProfessionalAreaError(Exception):
    pass


class ProfessionalAssignmentService:

    def __init__(
        self,
        professional_repository: ProfessionalRepository,
        service_repository: ServiceRepository,
        assignment_repository: ProfessionalServiceRepository,
    ):
        self.professional_repository = professional_repository
        self.service_repository = service_repository
        self.assignment_repository = assignment_repository

    async def assign(
        self,
        professional_id: int,
        service_id: int,
    ) -> None:

        professional = await self.professional_repository.get_by_id(
            professional_id
        )

        if professional is None:
            raise AssignmentProfessionalNotFoundError(
                "Professional not found."
            )

        service = await self.service_repository.get_by_id(
            service_id
        )

        if service is None:
            raise AssignmentServiceNotFoundError(
                "Service not found."
            )

        if service.area_id != professional.care_area_id:
            raise ServiceDoesNotBelongToProfessionalAreaError(
                "The service does not belong to the professional's care area."
            )

        already_assigned = await self.assignment_repository.exists(
            professional_id,
            service_id,
        )

        if already_assigned:
            raise ServiceAlreadyAssignedError(
                "Service is already assigned to this professional."
            )

        await self.assignment_repository.assign_service(
            professional_id,
            service_id,
        )

    async def list_services(
        self,
        professional_id: int,
    ) -> list[Service]:

        professional = await self.professional_repository.get_by_id(
            professional_id
        )

        if professional is None:
            raise AssignmentProfessionalNotFoundError(
                "Professional not found."
            )

        return await self.assignment_repository.get_services(
            professional_id
        )