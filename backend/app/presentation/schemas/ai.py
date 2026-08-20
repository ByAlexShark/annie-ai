from pydantic import BaseModel, Field

from app.presentation.schemas.ai_intent import AIIntentResult


class AIChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class AIProcessRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )

    phone: str = Field(
        ...,
        min_length=7,
        max_length=25,
    )


class AIChatResponse(BaseModel):
    response: str


class AIProcessResponse(BaseModel):
    analysis: AIIntentResult
    response: str