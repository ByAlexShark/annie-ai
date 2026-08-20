from datetime import date

from app.domain.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)
from app.infrastructure.database.models.conversation_session import (
    ConversationSession,
)


class ConversationSessionService:
    def __init__(
        self,
        repository: ConversationSessionRepository,
    ):
        self.repository = repository

    async def get_by_phone(
        self,
        phone: str,
    ) -> ConversationSession | None:
        normalized_phone = phone.strip()

        return await self.repository.get_by_phone(
            normalized_phone
        )

    async def start_waiting_patient_name(
        self,
        phone: str,
        service_id: int | None = None,
        requested_date: date | None = None,
    ) -> ConversationSession:
        normalized_phone = phone.strip()

        conversation = await self.repository.get_by_phone(
            normalized_phone
        )

        if conversation is None:
            conversation = ConversationSession(
                phone=normalized_phone,
                state="waiting_patient_name",
                service_id=service_id,
                requested_date=requested_date,
            )

            return await self.repository.create(
                conversation
            )

        conversation.state = "waiting_patient_name"
        conversation.service_id = service_id
        conversation.requested_date = requested_date
        conversation.professional_id = None

        return await self.repository.update(
            conversation
        )

    async def set_waiting_appointment_time(
        self,
        conversation: ConversationSession,
        patient_id: int,
        service_id: int,
        professional_id: int,
        requested_date: date,
    ) -> ConversationSession:
        conversation.state = "waiting_appointment_time"
        conversation.patient_id = patient_id
        conversation.service_id = service_id
        conversation.professional_id = professional_id
        conversation.requested_date = requested_date

        return await self.repository.update(
            conversation
        )

    async def reset(
        self,
        conversation: ConversationSession,
    ) -> ConversationSession:
        conversation.state = "idle"
        conversation.service_id = None
        conversation.professional_id = None
        conversation.requested_date = None

        return await self.repository.update(
            conversation
        )