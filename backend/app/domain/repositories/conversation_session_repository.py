from abc import ABC, abstractmethod

from app.infrastructure.database.models.conversation_session import (
    ConversationSession,
)


class ConversationSessionRepository(ABC):

    @abstractmethod
    async def get_by_phone(
        self,
        phone: str,
    ) -> ConversationSession | None:
        pass

    @abstractmethod
    async def create(
        self,
        conversation: ConversationSession,
    ) -> ConversationSession:
        pass

    @abstractmethod
    async def update(
        self,
        conversation: ConversationSession,
    ) -> ConversationSession:
        pass