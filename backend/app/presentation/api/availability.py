from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.availability_service import (
    AvailabilityProfessionalNotFoundError,
    AvailabilityService,
    AvailabilityServiceNotAssignedError,
)
from app.infrastructure.database.appointment_repository import (
    SQLAlchemyAppointmentRepository,
)
from app.infrastructure.database.professional_repository import (
    SQLAlchemyProfessionalRepository,
)
from app.infrastructure.database.professional_service_repository import (
    SQLAlchemyProfessionalServiceRepository,
)
from app.infrastructure.database.schedule_repository import (
    SQLAlchemyScheduleRepository,
)
from app.infrastructure.database.session import get_db
from app.presentation.schemas.availability import (
    AvailabilityResponse,
)


router = APIRouter(
    prefix="/availability",
    tags=["Availability"],
)


def get_availability_service(
    db: AsyncSession = Depends(get_db),
) -> AvailabilityService:

    return AvailabilityService(
        professional_repository=(
            SQLAlchemyProfessionalRepository(db)
        ),
        schedule_repository=(
            SQLAlchemyScheduleRepository(db)
        ),
        appointment_repository=(
            SQLAlchemyAppointmentRepository(db)
        ),
        professional_service_repository=(
            SQLAlchemyProfessionalServiceRepository(db)
        ),
    )


@router.get(
    "",
    response_model=AvailabilityResponse,
)
async def get_availability(
    professional_id: int = Query(gt=0),
    service_id: int = Query(gt=0),
    requested_date: date = Query(alias="date"),
    service: AvailabilityService = Depends(
        get_availability_service
    ),
):
    try:

        slots = await service.get_available_slots(
            professional_id=professional_id,
            service_id=service_id,
            requested_date=requested_date,
        )

        return AvailabilityResponse(
            professional_id=professional_id,
            service_id=service_id,
            date=requested_date,
            available_slots=slots,
        )

    except AvailabilityProfessionalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except AvailabilityServiceNotAssignedError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc