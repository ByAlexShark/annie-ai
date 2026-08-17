from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.appointment_service import (
    AppointmentInvalidScheduleError,
    AppointmentNotFoundError,
    AppointmentPatientNotFoundError,
    AppointmentProfessionalNotFoundError,
    AppointmentService,
    AppointmentServiceNotAssignedError,
    AppointmentServiceNotFoundError,
    AppointmentSlotUnavailableError,
    AppointmentInvalidStatusError,
)
from app.application.services.availability_service import (
    AvailabilityService,
)
from app.infrastructure.database.appointment_repository import (
    SQLAlchemyAppointmentRepository,
)
from app.infrastructure.database.patient_repository import (
    SQLAlchemyPatientRepository,
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
from app.infrastructure.database.service_repository import (
    SQLAlchemyServiceRepository,
)
from app.infrastructure.database.session import get_db
from app.presentation.schemas.appointment import (
    AppointmentCreate,
    AppointmentReschedule,
    AppointmentResponse,
)


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"],
)


def get_appointment_service(
    db: AsyncSession = Depends(get_db),
) -> AppointmentService:

    appointment_repository = (
        SQLAlchemyAppointmentRepository(db)
    )

    patient_repository = (
        SQLAlchemyPatientRepository(db)
    )

    professional_repository = (
        SQLAlchemyProfessionalRepository(db)
    )

    service_repository = (
        SQLAlchemyServiceRepository(db)
    )

    professional_service_repository = (
        SQLAlchemyProfessionalServiceRepository(db)
    )

    schedule_repository = (
        SQLAlchemyScheduleRepository(db)
    )

    availability_service = AvailabilityService(
        professional_repository=professional_repository,
        schedule_repository=schedule_repository,
        appointment_repository=appointment_repository,
        professional_service_repository=(
            professional_service_repository
        ),
    )

    return AppointmentService(
        appointment_repository=appointment_repository,
        patient_repository=patient_repository,
        professional_repository=professional_repository,
        service_repository=service_repository,
        professional_service_repository=(
            professional_service_repository
        ),
        schedule_repository=schedule_repository,
        availability_service=availability_service,
    )


@router.get(
    "",
    response_model=list[AppointmentResponse],
)
async def list_appointments(
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):
    return await service.list_appointments()


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse,
)
async def get_appointment(
    appointment_id: int,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):
    try:
        return await service.get_appointment(
            appointment_id
        )

    except AppointmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_appointment(
    data: AppointmentCreate,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):
    try:

        return await service.create_appointment(
            patient_id=data.patient_id,
            professional_id=data.professional_id,
            service_id=data.service_id,
            appointment_date=data.appointment_date,
            start_time=data.start_time,
            reason=data.reason,
            source=data.source,
        )

    except (
        AppointmentPatientNotFoundError,
        AppointmentProfessionalNotFoundError,
        AppointmentServiceNotFoundError,
    ) as exc:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (
        AppointmentServiceNotAssignedError,
        AppointmentSlotUnavailableError,
        AppointmentInvalidScheduleError,
    ) as exc:

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

@router.patch(
    "/{appointment_id}/cancel",
    response_model=AppointmentResponse,
)
async def cancel_appointment(
    appointment_id: int,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):
    try:
        return await service.cancel_appointment(
            appointment_id
        )

    except AppointmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except AppointmentInvalidStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    
@router.patch(
    "/{appointment_id}/reschedule",
    response_model=AppointmentResponse,
)
async def reschedule_appointment(
    appointment_id: int,
    data: AppointmentReschedule,
    service: AppointmentService = Depends(
        get_appointment_service
    ),
):
    try:
        return await service.reschedule_appointment(
            appointment_id=appointment_id,
            appointment_date=data.appointment_date,
            start_time=data.start_time,
        )

    except AppointmentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except (
        AppointmentInvalidStatusError,
        AppointmentSlotUnavailableError,
        AppointmentInvalidScheduleError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc