from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.care_area_service import (
    CareAreaAlreadyExistsError,
    CareAreaNotFoundError,
    CareAreaService,
)
from app.infrastructure.database.care_area_repository import (
    SQLAlchemyCareAreaRepository,
)
from app.infrastructure.database.session import get_db
from app.presentation.schemas.care_area import (
    CareAreaCreate,
    CareAreaResponse,
)


router = APIRouter(
    prefix="/areas",
    tags=["Care Areas"],
)


def get_care_area_service(
    db: AsyncSession = Depends(get_db),
) -> CareAreaService:

    repository = SQLAlchemyCareAreaRepository(db)

    return CareAreaService(repository)


@router.get(
    "",
    response_model=list[CareAreaResponse],
)
async def list_care_areas(
    service: CareAreaService = Depends(get_care_area_service),
):
    return await service.list_areas()


@router.get(
    "/{area_id}",
    response_model=CareAreaResponse,
)
async def get_care_area(
    area_id: int,
    service: CareAreaService = Depends(get_care_area_service),
):
    try:
        return await service.get_area(area_id)

    except CareAreaNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=CareAreaResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_care_area(
    data: CareAreaCreate,
    service: CareAreaService = Depends(get_care_area_service),
):
    try:
        return await service.create_area(
            name=data.name,
            description=data.description,
        )

    except CareAreaAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
