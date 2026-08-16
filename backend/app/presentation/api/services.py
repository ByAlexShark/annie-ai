from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.service_service import (
    InvalidCareAreaError,
    ServiceAlreadyExistsError,
    ServiceNotFoundError,
    ServiceService,
)
from app.infrastructure.database.care_area_repository import (
    SQLAlchemyCareAreaRepository,
)
from app.infrastructure.database.service_repository import (
    SQLAlchemyServiceRepository,
)
from app.infrastructure.database.session import get_db
from app.presentation.schemas.service import (
    ServiceCreate,
    ServiceResponse,
)


router = APIRouter(
    tags=["Services"],
)


def get_service_service(
    db: AsyncSession = Depends(get_db),
) -> ServiceService:

    service_repository = SQLAlchemyServiceRepository(db)

    area_repository = SQLAlchemyCareAreaRepository(db)

    return ServiceService(
        service_repository=service_repository,
        care_area_repository=area_repository,
    )


@router.get(
    "/services",
    response_model=list[ServiceResponse],
)
async def list_services(
    area_id: int | None = Query(
        default=None,
        gt=0,
    ),
    service: ServiceService = Depends(
        get_service_service
    ),
):
    try:
        return await service.list_services(
            area_id=area_id
        )

    except InvalidCareAreaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/services/{service_id}",
    response_model=ServiceResponse,
)
async def get_service(
    service_id: int,
    service: ServiceService = Depends(
        get_service_service
    ),
):
    try:
        return await service.get_service(
            service_id
        )

    except ServiceNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/areas/{area_id}/services",
    response_model=list[ServiceResponse],
)
async def list_services_by_area(
    area_id: int,
    service: ServiceService = Depends(
        get_service_service
    ),
):
    try:
        return await service.list_services(
            area_id=area_id
        )

    except InvalidCareAreaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {
            "description": "Care area not found"
        },
        409: {
            "description": "Service already exists"
        },
    },
)
async def create_service(
    data: ServiceCreate,
    service: ServiceService = Depends(
        get_service_service
    ),
):
    try:
        return await service.create_service(
            area_id=data.area_id,
            name=data.name,
            description=data.description,
            default_duration_minutes=(
                data.default_duration_minutes
            ),
            price=data.price,
            currency=data.currency,
        )

    except InvalidCareAreaError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ServiceAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc