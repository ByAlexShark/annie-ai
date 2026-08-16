from fastapi import FastAPI

from app.core.config import settings
from app.presentation.api.router import api_router


app = FastAPI(
    title=settings.app_name,
    description=(
        "Plataforma inteligente multimodal de atención, "
        "gestión de citas y derivación médica."
    ),
    version="0.1.0",
)


app.include_router(api_router)


@app.get(
    "/",
    tags=["System"],
)
async def root():
    return {
        "application": settings.app_name,
        "status": "running",
        "environment": settings.app_env,
        "version": "0.1.0",
    }


@app.get(
    "/health",
    tags=["System"],
)
async def health_check():
    return {
        "status": "healthy"
    }
