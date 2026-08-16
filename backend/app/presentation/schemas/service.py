from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ServiceCreate(BaseModel):

    area_id: int = Field(
        gt=0
    )

    name: str = Field(
        min_length=2,
        max_length=120,
        examples=["Cardiología"],
    )

    description: str | None = Field(
        default=None,
        max_length=500,
    )

    default_duration_minutes: int = Field(
        default=30,
        ge=5,
        le=240,
    )

    price: Decimal | None = Field(
        default=None,
        ge=0,
    )

    currency: str = Field(
        default="BOB",
        min_length=3,
        max_length=3,
    )


class ServiceResponse(BaseModel):

    id: int
    area_id: int

    name: str
    description: str | None

    default_duration_minutes: int

    price: Decimal | None
    currency: str

    active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )