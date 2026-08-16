from pydantic import BaseModel, Field


class ProfessionalServiceAssign(BaseModel):
    service_id: int = Field(gt=0)


class ProfessionalServiceAssignResponse(BaseModel):
    professional_id: int
    service_id: int
    assigned: bool