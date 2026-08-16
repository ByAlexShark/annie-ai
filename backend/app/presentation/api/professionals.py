from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.professional_service import (
    ProfessionalCareAreaNotFoundError,
    ProfessionalNotFoundError,
    ProfessionalService,
)
from app.infrastructure.database.care_area_repository import (
    SQLAlchemyCareAreaRepository,
)
from app.infrastructure.database.professional_repository import (
    SQLAlchemyProfessionalRepository,
)
from app.infrastructure.database.session import get_db
from app.presentation.schemas.professional import (
    ProfessionalCreate,
    ProfessionalResponse,
)


router = APIRouter(
    prefix="/professionals",
    tags=["Professionals"],
)


def get_professional_service(
    db: AsyncSession = Depends(get_db),
) -> ProfessionalService:

    professional_repository = (
        SQLAlchemyProfessionalRepository(db)
    )

    care_area_repository = (
        SQLAlchemyCareAreaRepository(db)
    )

    return ProfessionalService(
        professional_repository=professional_repository,
        care_area_repository=care_area_repository,
    )


@router.get(
    "",
    response_model=list[ProfessionalResponse],
)
async def list_professionals(
    care_area_id: int | None = Query(
        default=None,
        gt=0,
    ),
    service: ProfessionalService = Depends(
        get_professional_service
    ),
):
    try:
        return await service.list_professionals(
            care_area_id=care_area_id
        )

    except ProfessionalCareAreaNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{professional_id}",
    response_model=ProfessionalResponse,
)
async def get_professional(
    professional_id: int,
    service: ProfessionalService = Depends(
        get_professional_service
    ),
):
    try:
        return await service.get_professional(
            professional_id
        )

    except ProfessionalNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=ProfessionalResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {
            "description": "Care area not found"
        }
    },
)
async def create_professional(
    data: ProfessionalCreate,
    service: ProfessionalService = Depends(
        get_professional_service
    ),
):
    try:
        return await service.create_professional(
            care_area_id=data.care_area_id,
            first_name=data.first_name,
            last_name=data.last_name,
            license_number=data.license_number,
            phone=data.phone,
        )

    except ProfessionalCareAreaNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc