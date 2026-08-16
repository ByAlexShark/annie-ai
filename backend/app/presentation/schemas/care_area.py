from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CareAreaCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Especialidades Médicas"],
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )


class CareAreaResponse(BaseModel):
    id: int
    name: str
    description: str | None
    active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
