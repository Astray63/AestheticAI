"""
Schémas Pydantic centralisés
Exportation de tous les schémas de l'application
"""

from .user import (
    UserBase, UserCreate, UserUpdate, UserResponse, 
    UserLogin, TokenResponse
)
from .patient import (
    PatientBase, PatientCreate, PatientUpdate, 
    PatientResponse, PatientSummary
)
from .simulation import (
    SimulationBase, SimulationCreate, SimulationUpdate,
    SimulationResponse, SimulationSummary, SimulationStats,
    InterventionTypeInfo, AvailableInterventions
)

# Schémas génériques
from pydantic import BaseModel
from typing import List, Any, Optional


class SuccessResponse(BaseModel):
    """Schéma de réponse générique pour les succès"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Schéma de réponse générique pour les erreurs"""
    success: bool = False
    error: str
    details: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Schéma de réponse paginée"""
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int


class HealthCheckResponse(BaseModel):
    """Schéma pour le health check"""
    status: str = "healthy"
    version: str
    timestamp: str
    environment: str


# Export de tous les schémas
__all__ = [
    # User schemas
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", 
    "UserLogin", "TokenResponse",
    
    # Patient schemas
    "PatientBase", "PatientCreate", "PatientUpdate", 
    "PatientResponse", "PatientSummary",
    
    # Simulation schemas
    "SimulationBase", "SimulationCreate", "SimulationUpdate",
    "SimulationResponse", "SimulationSummary", "SimulationStats",
    "InterventionTypeInfo", "AvailableInterventions",
    
    # Generic schemas
    "SuccessResponse", "ErrorResponse", "PaginatedResponse", 
    "HealthCheckResponse"
]
