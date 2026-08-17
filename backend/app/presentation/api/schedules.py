from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.schedule_service import (
    InvalidScheduleError,
    ScheduleProfessionalNotFoundError,
    ScheduleService,
)
from app.infrastructure.database.professional_repository import (
    SQLAlchemyProfessionalRepository,
)
from app.infrastructure.database.schedule_repository import (
    SQLAlchemyScheduleRepository,
)
from app.infrastructure.database.session import get_db
from app.presentation.schemas.schedule import (
    ScheduleCreate,
    ScheduleResponse,
)


router = APIRouter(
    prefix="/professionals",
    tags=["Schedules"],
)


def get_schedule_service(
    db: AsyncSession = Depends(get_db),
) -> ScheduleService:

    return ScheduleService(
        schedule_repository=(
            SQLAlchemyScheduleRepository(db)
        ),
        professional_repository=(
            SQLAlchemyProfessionalRepository(db)
        ),
    )


@router.get(
    "/{professional_id}/schedules",
    response_model=list[ScheduleResponse],
)
async def list_schedules(
    professional_id: int,
    service: ScheduleService = Depends(
        get_schedule_service
    ),
):
    try:
        return await service.list_schedules(
            professional_id
        )

    except ScheduleProfessionalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{professional_id}/schedules",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_schedule(
    professional_id: int,
    data: ScheduleCreate,
    service: ScheduleService = Depends(
        get_schedule_service
    ),
):
    try:
        return await service.create_schedule(
            professional_id=professional_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            appointment_duration_minutes=(
                data.appointment_duration_minutes
            ),
            max_appointments=data.max_appointments,
        )

    except ScheduleProfessionalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except InvalidScheduleError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc