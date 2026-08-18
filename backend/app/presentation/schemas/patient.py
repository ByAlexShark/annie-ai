from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class PatientCreate(BaseModel):

    phone: str = Field(
        min_length=7,
        max_length=25,
        examples=["79717723"],
    )

    first_name: str | None = Field(
        default=None,
        max_length=100,
    )

    last_name: str | None = Field(
        default=None,
        max_length=100,
    )

    document_number: str | None = Field(
        default=None,
        max_length=30,
    )

    birth_date: date | None = None


class PatientResponse(BaseModel):

    id: int
    phone: str

    first_name: str | None
    last_name: str | None

    document_number: str | None
    birth_date: date | None

    active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )