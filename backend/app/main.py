from fastapi import FastAPI

from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description="Plataforma inteligente de atención y gestión médica.",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {
        "application": settings.app_name,
        "status": "running",
        "environment": settings.app_env,
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }
