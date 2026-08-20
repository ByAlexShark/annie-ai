from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.ai_agent_service import AIAgentService
from app.application.services.availability_service import AvailabilityService
from app.application.services.date_resolution_service import DateResolutionService
from app.application.services.service_service import ServiceService

from app.infrastructure.database.appointment_repository import (
    SQLAlchemyAppointmentRepository,
)
from app.infrastructure.database.care_area_repository import (
    SQLAlchemyCareAreaRepository,
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

from app.presentation.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIProcessResponse,
)
from app.presentation.schemas.ai_intent import AIIntentResult


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)

ai_agent = AIAgentService()


def get_service_service(
    db: AsyncSession = Depends(get_db),
) -> ServiceService:
    service_repository = SQLAlchemyServiceRepository(db)
    area_repository = SQLAlchemyCareAreaRepository(db)

    return ServiceService(
        service_repository=service_repository,
        care_area_repository=area_repository,
    )


def get_availability_service(
    db: AsyncSession = Depends(get_db),
) -> AvailabilityService:
    return AvailabilityService(
        professional_repository=SQLAlchemyProfessionalRepository(db),
        schedule_repository=SQLAlchemyScheduleRepository(db),
        appointment_repository=SQLAlchemyAppointmentRepository(db),
        professional_service_repository=(
            SQLAlchemyProfessionalServiceRepository(db)
        ),
    )


@router.post(
    "/chat",
    response_model=AIChatResponse,
)
async def chat_with_ai(
    request: AIChatRequest,
) -> AIChatResponse:
    try:
        response = await ai_agent.chat(
            request.message
        )

        return AIChatResponse(
            response=response,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "El servicio de inteligencia artificial "
                "no está disponible."
            ),
        ) from exc


@router.post(
    "/analyze",
    response_model=AIIntentResult,
)
async def analyze_message(
    request: AIChatRequest,
    service_service: ServiceService = Depends(
        get_service_service
    ),
) -> AIIntentResult:
    try:
        services = await service_service.list_services()

        service_catalog = [
            {
                "id": service.id,
                "name": service.name,
            }
            for service in services
            if service.active
        ]

        result = await ai_agent.analyze_message(
            message=request.message,
            services=service_catalog,
        )

        return AIIntentResult(**result)

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo analizar el mensaje.",
        ) from exc


@router.post(
    "/process",
    response_model=AIProcessResponse,
)
async def process_message(
    request: AIChatRequest,
    service_service: ServiceService = Depends(
        get_service_service
    ),
    availability_service: AvailabilityService = Depends(
        get_availability_service
    ),
) -> AIProcessResponse:
    try:
        services = await service_service.list_services()

        service_catalog = [
            {
                "id": service.id,
                "name": service.name,
            }
            for service in services
            if service.active
        ]

        analysis = await ai_agent.analyze_message(
            message=request.message,
            services=service_catalog,
        )

        if (
            analysis.get("intent") == "book_appointment"
            and analysis.get("service_id") is not None
            and not analysis.get("needs_clarification")
        ):
            requested_date_text = analysis.get(
                "requested_date"
            )

            if requested_date_text is None:
                patient_response = (
                    "Entendido. ¿Para qué día deseas "
                    "agendar tu cita?"
                )

            else:
                date_resolver = DateResolutionService()

                resolved_date = date_resolver.resolve(
                    requested_date_text
                )

                if resolved_date is None:
                    patient_response = (
                        "No pude identificar la fecha "
                        "de la cita. "
                        "Puedes indicarme, por ejemplo, "
                        "'mañana', 'lunes' o una fecha "
                        "específica."
                    )

                else:
                    availability = (
                        await availability_service
                        .get_available_slots_by_service(
                            service_id=analysis[
                                "service_id"
                            ],
                            requested_date=resolved_date,
                        )
                    )

                    if availability:
                        availability_parts = []

                        for item in availability:
                            slots = ", ".join(
                                item[
                                    "available_slots"
                                ][:8]
                            )

                            availability_parts.append(
                                (
                                    f"{item['professional_name']}: "
                                    f"{slots}"
                                )
                            )

                        availability_text = " | ".join(
                            availability_parts
                        )

                        patient_response = (
                            f"Tenemos disponibilidad para "
                            f"{analysis['service_name']} "
                            f"el "
                            f"{resolved_date.strftime('%d/%m/%Y')}. "
                            f"{availability_text}. "
                            "¿Qué horario prefieres?"
                        )

                    else:
                        patient_response = (
                            f"No encontré horarios "
                            f"disponibles para "
                            f"{analysis['service_name']} "
                            f"el "
                            f"{resolved_date.strftime('%d/%m/%Y')}. "
                            "¿Deseas consultar otro día?"
                        )

        else:
            patient_response = (
                await ai_agent.build_patient_response(
                    message=request.message,
                    analysis=analysis,
                    services=service_catalog,
                )
            )

        return AIProcessResponse(
            analysis=AIIntentResult(**analysis),
            response=patient_response,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="No se pudo procesar el mensaje.",
        ) from exc