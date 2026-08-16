from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.professional_assignment_service import (
    AssignmentProfessionalNotFoundError,
    AssignmentServiceNotFoundError,
    ProfessionalAssignmentService,
    ServiceAlreadyAssignedError,
    ServiceDoesNotBelongToProfessionalAreaError,
)
from app.infrastructure.database.professional_repository import (
    SQLAlchemyProfessionalRepository,
)
from app.infrastructure.database.professional_service_repository import (
    SQLAlchemyProfessionalServiceRepository,
)
from app.infrastructure.database.service_repository import (
    SQLAlchemyServiceRepository,
)
from app.infrastructure.database.session import get_db
from app.presentation.schemas.professional_service import (
    ProfessionalServiceAssign,
    ProfessionalServiceAssignResponse,
)
from app.presentation.schemas.service import ServiceResponse


router = APIRouter(
    prefix="/professionals",
    tags=["Professional Services"],
)


def get_assignment_service(
    db: AsyncSession = Depends(get_db),
) -> ProfessionalAssignmentService:

    return ProfessionalAssignmentService(
        professional_repository=SQLAlchemyProfessionalRepository(db),
        service_repository=SQLAlchemyServiceRepository(db),
        assignment_repository=SQLAlchemyProfessionalServiceRepository(db),
    )


@router.post(
    "/{professional_id}/services",
    response_model=ProfessionalServiceAssignResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_service(
    professional_id: int,
    data: ProfessionalServiceAssign,
    service: ProfessionalAssignmentService = Depends(
        get_assignment_service
    ),
):
    try:
        await service.assign(
            professional_id=professional_id,
            service_id=data.service_id,
        )

        return {
            "professional_id": professional_id,
            "service_id": data.service_id,
            "assigned": True,
        }

    except (
        AssignmentProfessionalNotFoundError,
        AssignmentServiceNotFoundError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (
        ServiceAlreadyAssignedError,
        ServiceDoesNotBelongToProfessionalAreaError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.get(
    "/{professional_id}/services",
    response_model=list[ServiceResponse],
)
async def list_professional_services(
    professional_id: int,
    service: ProfessionalAssignmentService = Depends(
        get_assignment_service
    ),
):
    try:
        return await service.list_services(
            professional_id
        )

    except AssignmentProfessionalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc