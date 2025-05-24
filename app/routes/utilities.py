from fastapi import Depends

from app.config import Settings, get_settings
from app.main import app


@app.get("/health")
async def health_check(settings: Settings = Depends(get_settings)):
    return {
        "status": "healthy",
        "environment": settings.environment,
        "debug": settings.debug,
        "api_prefix": settings.api_prefix
    }


@app.get("/config/info")
async def config_info(settings: Settings = Depends(get_settings)):
    """Endpoint to view configuration (without secrets)"""
    return {
        "environment": settings.environment,
        "debug": settings.debug,
        "api_prefix": settings.api_prefix,
        "number_of_classes": settings.number_of_classes,
        "threshold": settings.wildlens_footprint_binary_classification_threshold,
        "mime_types": settings.prediction_authorized_mime_types,
        "token_expire_minutes": settings.access_token_expire_minutes,
    }