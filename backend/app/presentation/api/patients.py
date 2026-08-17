from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.patient_service import (
    PatientAlreadyExistsError,
    PatientNotFoundError,
    PatientService,
)
from app.infrastructure.database.patient_repository import (
    SQLAlchemyPatientRepository,
)
from app.infrastructure.database.session import get_db
from app.presentation.schemas.patient import (
    PatientCreate,
    PatientResponse,
)


router = APIRouter(
    prefix="/patients",
    tags=["Patients"],
)


def get_patient_service(
    db: AsyncSession = Depends(get_db),
) -> PatientService:

    return PatientService(
        SQLAlchemyPatientRepository(db)
    )


@router.get(
    "",
    response_model=list[PatientResponse],
)
async def list_patients(
    service: PatientService = Depends(
        get_patient_service
    ),
):
    return await service.list_patients()


@router.get(
    "/{patient_id}",
    response_model=PatientResponse,
)
async def get_patient(
    patient_id: int,
    service: PatientService = Depends(
        get_patient_service
    ),
):
    try:
        return await service.get_patient(
            patient_id
        )

    except PatientNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {
            "description": "Phone already registered"
        }
    },
)
async def create_patient(
    data: PatientCreate,
    service: PatientService = Depends(
        get_patient_service
    ),
):
    try:
        return await service.create_patient(
            phone=data.phone,
            first_name=data.first_name,
            last_name=data.last_name,
            document_number=data.document_number,
            birth_date=data.birth_date,
        )

    except PatientAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc