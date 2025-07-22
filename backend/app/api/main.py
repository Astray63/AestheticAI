"""API endpoints principaux et utilitaires"""

from fastapi import APIRouter, status
from datetime import datetime

from app.core.config import settings
from app.schemas import HealthCheckResponse, SuccessResponse

router = APIRouter(tags=["System"])


@router.get("/", response_model=SuccessResponse)
async def root():
    """
    Point d'entrée de l'API
    
    Retourne les informations de base de l'API
    AestheticAI pour vérifier que l'application fonctionne.
    """
    return SuccessResponse(
        message=f"Bienvenue sur {settings.app_name} API v{settings.app_version}",
        data={
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "documentation": "/docs"
        }
    )


@router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Vérification de santé de l'API
    
    Endpoint utilisé par les systèmes de monitoring
    et les load balancers pour vérifier le statut de l'application.
    """
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now().isoformat(),
        environment=settings.environment
    )


@router.get("/version", response_model=dict)
async def get_version():
    """
    Obtenir la version de l'API
    
    Retourne les informations détaillées de version
    et de configuration de l'application.
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "debug": settings.debug,
        "device": settings.device,
        "model_name": settings.model_name
    }
