from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProfessionalCreate(BaseModel):

    care_area_id: int = Field(gt=0)

    first_name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Carlos"],
    )

    last_name: str = Field(
        min_length=2,
        max_length=100,
        examples=["Mendoza"],
    )

    license_number: str | None = Field(
        default=None,
        max_length=50,
    )

    phone: str | None = Field(
        default=None,
        max_length=25,
    )


class ProfessionalResponse(BaseModel):

    id: int
    care_area_id: int

    first_name: str
    last_name: str

    license_number: str | None
    phone: str | None

    active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )