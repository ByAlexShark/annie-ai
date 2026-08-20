from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.ai_agent_service import AIAgentService
from app.application.services.appointment_service import (
    AppointmentInvalidScheduleError,
    AppointmentService,
    AppointmentSlotUnavailableError,
)
from app.application.services.availability_service import AvailabilityService
from app.application.services.conversation_session_service import (
    ConversationSessionService,
)
from app.application.services.date_resolution_service import (
    DateResolutionService,
)
from app.application.services.patient_service import PatientService
from app.application.services.service_service import ServiceService
from app.application.services.time_resolution_service import (
    TimeResolutionService,
)

from app.infrastructure.database.appointment_repository import (
    SQLAlchemyAppointmentRepository,
)
from app.infrastructure.database.care_area_repository import (
    SQLAlchemyCareAreaRepository,
)
from app.infrastructure.database.conversation_session_repository import (
    SQLAlchemyConversationSessionRepository,
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

from app.presentation.schemas.ai import (
    AIChatRequest,
    AIChatResponse,
    AIProcessRequest,
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


def get_patient_service(
    db: AsyncSession = Depends(get_db),
) -> PatientService:
    return PatientService(
        repository=SQLAlchemyPatientRepository(db),
    )


def get_conversation_session_service(
    db: AsyncSession = Depends(get_db),
) -> ConversationSessionService:
    return ConversationSessionService(
        repository=SQLAlchemyConversationSessionRepository(db),
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


def get_appointment_service(
    db: AsyncSession = Depends(get_db),
) -> AppointmentService:
    appointment_repository = SQLAlchemyAppointmentRepository(db)
    patient_repository = SQLAlchemyPatientRepository(db)
    professional_repository = SQLAlchemyProfessionalRepository(db)
    service_repository = SQLAlchemyServiceRepository(db)

    professional_service_repository = (
        SQLAlchemyProfessionalServiceRepository(db)
    )

    schedule_repository = SQLAlchemyScheduleRepository(db)

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
    request: AIProcessRequest,
    service_service: ServiceService = Depends(
        get_service_service
    ),
    availability_service: AvailabilityService = Depends(
        get_availability_service
    ),
    patient_service: PatientService = Depends(
        get_patient_service
    ),
    conversation_service: ConversationSessionService = Depends(
        get_conversation_session_service
    ),
    appointment_service: AppointmentService = Depends(
        get_appointment_service
    ),
) -> AIProcessResponse:
    try:
        patient = await patient_service.get_patient_by_phone(
            request.phone
        )

        conversation = await conversation_service.get_by_phone(
            request.phone
        )

        services = await service_service.list_services()

        service_catalog = [
            {
                "id": service.id,
                "name": service.name,
            }
            for service in services
            if service.active
        ]

        # --------------------------------------------------
        # ESPERANDO QUE EL PACIENTE ELIJA UNA HORA
        # --------------------------------------------------
        if (
            conversation is not None
            and conversation.state == "waiting_appointment_time"
            and patient is not None
        ):
            service_id = conversation.service_id
            professional_id = conversation.professional_id
            requested_date = conversation.requested_date

            if (
                service_id is None
                or professional_id is None
                or requested_date is None
            ):
                await conversation_service.reset(
                    conversation
                )

                return AIProcessResponse(
                    analysis=AIIntentResult(
                        intent="book_appointment",
                        service_id=service_id,
                        service_name=None,
                        requested_date=None,
                        needs_clarification=True,
                        needs_human=False,
                    ),
                    response=(
                        "No pude recuperar todos los datos "
                        "de la cita. Indícame nuevamente "
                        "qué servicio deseas agendar."
                    ),
                )

            service_name = next(
                (
                    service["name"]
                    for service in service_catalog
                    if service["id"] == service_id
                ),
                None,
            )

            time_resolver = TimeResolutionService()

            selected_time = time_resolver.resolve(
                request.message
            )

            if selected_time is None:
                return AIProcessResponse(
                    analysis=AIIntentResult(
                        intent="book_appointment",
                        service_id=service_id,
                        service_name=service_name,
                        requested_date=requested_date.isoformat(),
                        needs_clarification=False,
                        needs_human=False,
                    ),
                    response=(
                        "No pude identificar el horario. "
                        "Puedes responder, por ejemplo, "
                        "'09:30' o '10:00'."
                    ),
                )

            try:
                appointment = (
                    await appointment_service.create_appointment(
                        patient_id=patient.id,
                        professional_id=professional_id,
                        service_id=service_id,
                        appointment_date=requested_date,
                        start_time=selected_time,
                        reason=None,
                        source="whatsapp",
                    )
                )

            except (
                AppointmentSlotUnavailableError,
                AppointmentInvalidScheduleError,
            ):
                available_slots = (
                    await availability_service.get_available_slots(
                        professional_id=professional_id,
                        service_id=service_id,
                        requested_date=requested_date,
                    )
                )

                if available_slots:
                    slots_text = ", ".join(
                        available_slots[:8]
                    )

                    response_text = (
                        "Ese horario no está disponible. "
                        f"Los horarios disponibles son: "
                        f"{slots_text}. "
                        "¿Cuál prefieres?"
                    )

                else:
                    response_text = (
                        "Ese horario no está disponible "
                        "y no quedan horarios libres para ese día. "
                        "¿Deseas consultar otra fecha?"
                    )

                return AIProcessResponse(
                    analysis=AIIntentResult(
                        intent="book_appointment",
                        service_id=service_id,
                        service_name=service_name,
                        requested_date=requested_date.isoformat(),
                        needs_clarification=False,
                        needs_human=False,
                    ),
                    response=response_text,
                )

            await conversation_service.reset(
                conversation
            )

            return AIProcessResponse(
                analysis=AIIntentResult(
                    intent="book_appointment",
                    service_id=service_id,
                    service_name=service_name,
                    requested_date=requested_date.isoformat(),
                    needs_clarification=False,
                    needs_human=False,
                ),
                response=(
                    f"Tu cita para {service_name} quedó confirmada "
                    f"para el "
                    f"{requested_date.strftime('%d/%m/%Y')} "
                    f"a las {selected_time.strftime('%H:%M')}. "
                    f"Tu número de cita es {appointment.id}."
                ),
            )

        # --------------------------------------------------
        # ESPERANDO NOMBRE DE PACIENTE NUEVO
        # --------------------------------------------------
        if (
            conversation is not None
            and conversation.state == "waiting_patient_name"
            and patient is None
        ):
            full_name = request.message.strip()

            name_parts = full_name.split(
                maxsplit=1
            )

            first_name = name_parts[0]

            last_name = (
                name_parts[1]
                if len(name_parts) > 1
                else None
            )

            patient = await patient_service.create_patient(
                phone=request.phone,
                first_name=first_name,
                last_name=last_name,
            )

            service_id = conversation.service_id
            requested_date = conversation.requested_date

            if (
                service_id is None
                or requested_date is None
            ):
                await conversation_service.reset(
                    conversation
                )

                return AIProcessResponse(
                    analysis=AIIntentResult(
                        intent="book_appointment",
                        service_id=service_id,
                        service_name=None,
                        requested_date=None,
                        needs_clarification=True,
                        needs_human=False,
                    ),
                    response=(
                        f"Gracias, {first_name}. "
                        "Tu registro fue creado correctamente. "
                        "¿Qué servicio deseas solicitar?"
                    ),
                )

            service_name = next(
                (
                    service["name"]
                    for service in service_catalog
                    if service["id"] == service_id
                ),
                None,
            )

            availability = (
                await availability_service
                .get_available_slots_by_service(
                    service_id=service_id,
                    requested_date=requested_date,
                )
            )

            if not availability:
                await conversation_service.reset(
                    conversation
                )

                return AIProcessResponse(
                    analysis=AIIntentResult(
                        intent="book_appointment",
                        service_id=service_id,
                        service_name=service_name,
                        requested_date=requested_date.isoformat(),
                        needs_clarification=False,
                        needs_human=False,
                    ),
                    response=(
                        f"Gracias, {first_name}. "
                        "Tu registro fue creado correctamente. "
                        f"No encontré horarios disponibles para "
                        f"{service_name} el "
                        f"{requested_date.strftime('%d/%m/%Y')}. "
                        "¿Deseas consultar otro día?"
                    ),
                )

            selected_professional = availability[0]

            await conversation_service.set_waiting_appointment_time(
                conversation=conversation,
                patient_id=patient.id,
                service_id=service_id,
                professional_id=selected_professional[
                    "professional_id"
                ],
                requested_date=requested_date,
            )

            slots = ", ".join(
                selected_professional[
                    "available_slots"
                ][:8]
            )

            return AIProcessResponse(
                analysis=AIIntentResult(
                    intent="book_appointment",
                    service_id=service_id,
                    service_name=service_name,
                    requested_date=requested_date.isoformat(),
                    needs_clarification=False,
                    needs_human=False,
                ),
                response=(
                    f"Gracias, {first_name}. "
                    "Tu registro fue creado correctamente. "
                    f"Tenemos disponibilidad para "
                    f"{service_name} el "
                    f"{requested_date.strftime('%d/%m/%Y')}. "
                    f"{selected_professional['professional_name']}: "
                    f"{slots}. "
                    "¿Qué horario prefieres?"
                ),
            )

        # --------------------------------------------------
        # MENSAJE NUEVO
        # --------------------------------------------------
        analysis = await ai_agent.analyze_message(
            message=request.message,
            services=service_catalog,
        )

        # --------------------------------------------------
        # PACIENTE NO REGISTRADO
        # --------------------------------------------------
        if patient is None:
            resolved_date = None

            requested_date_text = analysis.get(
                "requested_date"
            )

            if requested_date_text is not None:
                date_resolver = DateResolutionService()

                resolved_date = date_resolver.resolve(
                    requested_date_text
                )

            await conversation_service.start_waiting_patient_name(
                phone=request.phone,
                service_id=analysis.get("service_id"),
                requested_date=resolved_date,
            )

            return AIProcessResponse(
                analysis=AIIntentResult(**analysis),
                response=(
                    "Para continuar necesito registrarte "
                    "como paciente. "
                    "¿Cuál es tu nombre y apellido?"
                ),
            )

        # --------------------------------------------------
        # PACIENTE EXISTENTE QUIERE RESERVAR
        # --------------------------------------------------
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
                        "'mañana', 'lunes' o una fecha específica."
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
                        selected_professional = availability[0]

                        if conversation is None:
                            conversation = (
                                await conversation_service
                                .start_waiting_patient_name(
                                    phone=request.phone,
                                    service_id=analysis[
                                        "service_id"
                                    ],
                                    requested_date=resolved_date,
                                )
                            )

                        await conversation_service.set_waiting_appointment_time(
                            conversation=conversation,
                            patient_id=patient.id,
                            service_id=analysis[
                                "service_id"
                            ],
                            professional_id=selected_professional[
                                "professional_id"
                            ],
                            requested_date=resolved_date,
                        )

                        slots = ", ".join(
                            selected_professional[
                                "available_slots"
                            ][:8]
                        )

                        patient_response = (
                            f"Tenemos disponibilidad para "
                            f"{analysis['service_name']} "
                            f"el "
                            f"{resolved_date.strftime('%d/%m/%Y')}. "
                            f"{selected_professional['professional_name']}: "
                            f"{slots}. "
                            "¿Qué horario prefieres?"
                        )

                    else:
                        patient_response = (
                            f"No encontré horarios disponibles para "
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