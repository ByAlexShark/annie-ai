from fastapi import APIRouter

from app.presentation.api.care_areas import (
    router as care_areas_router,
)
from app.presentation.api.professionals import (
    router as professionals_router,
)
from app.presentation.api.services import (
    router as services_router,
)
from app.presentation.api.professional_services import (
    router as professional_services_router,
)


api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(
    care_areas_router
)

api_router.include_router(
    services_router
)

api_router.include_router(
    professionals_router
)

api_router.include_router(
    professional_services_router
)