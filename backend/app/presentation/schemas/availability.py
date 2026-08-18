from datetime import date

from pydantic import BaseModel


class AvailabilityResponse(BaseModel):
    professional_id: int
    service_id: int
    date: date
    available_slots: list[str]