from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field


class ScheduleCreate(BaseModel):

    day_of_week: int = Field(
        ge=0,
        le=6,
        description="0=Lunes, 6=Domingo",
    )

    start_time: time

    end_time: time

    appointment_duration_minutes: int = Field(
        default=30,
        ge=5,
        le=240,
    )

    max_appointments: int | None = Field(
        default=None,
        gt=0,
    )


class ScheduleResponse(BaseModel):

    id: int
    professional_id: int

    day_of_week: int

    start_time: time
    end_time: time

    appointment_duration_minutes: int
    max_appointments: int | None

    active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )