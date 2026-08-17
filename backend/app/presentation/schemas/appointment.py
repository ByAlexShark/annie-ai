from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums.appointment_status import (
    AppointmentStatus,
)


class AppointmentCreate(BaseModel):

    patient_id: int = Field(gt=0)

    professional_id: int = Field(gt=0)

    service_id: int = Field(gt=0)

    appointment_date: date

    start_time: time

    reason: str | None = Field(
        default=None,
        max_length=500,
    )

    source: str = Field(
        default="whatsapp",
        max_length=30,
    )


class AppointmentResponse(BaseModel):

    id: int

    patient_id: int
    professional_id: int
    service_id: int

    appointment_date: date

    start_time: time
    end_time: time

    status: AppointmentStatus

    source: str

    reason: str | None
    notes: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )