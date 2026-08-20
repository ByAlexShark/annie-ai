from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.conversation_session_repository import (
    ConversationSessionRepository,
)
from app.infrastructure.database.models.conversation_session import (
    ConversationSession,
)


class SQLAlchemyConversationSessionRepository(
    ConversationSessionRepository
):
    def __init__(
        self,
        session: AsyncSession,
    ):
        self.session = session

    async def get_by_phone(
        self,
        phone: str,
    ) -> ConversationSession | None:
        result = await self.session.execute(
            select(ConversationSession).where(
                ConversationSession.phone == phone
            )
        )

        return result.scalar_one_or_none()

    async def create(
        self,
        conversation: ConversationSession,
    ) -> ConversationSession:
        self.session.add(conversation)

        await self.session.commit()
        await self.session.refresh(conversation)

        return conversation

    async def update(
        self,
        conversation: ConversationSession,
    ) -> ConversationSession:
        await self.session.commit()
        await self.session.refresh(conversation)

        return conversation