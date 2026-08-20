from pydantic import BaseModel, Field

from app.presentation.schemas.ai_intent import AIIntentResult


class AIChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class AIChatResponse(BaseModel):
    response: str


class AIProcessResponse(BaseModel):
    analysis: AIIntentResult
    response: str