from typing import Literal

from pydantic import BaseModel


class AIIntentResult(BaseModel):
    intent: Literal[
        "book_appointment",
        "cancel_appointment",
        "reschedule_appointment",
        "ask_service",
        "greeting",
        "other",
    ]

    service_id: int | None = None
    service_name: str | None = None

    requested_date: str | None = None

    needs_clarification: bool = False
    needs_human: bool = False