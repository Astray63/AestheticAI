"""
Schémas Pydantic pour les simulations
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.core.config import INTERVENTION_TYPES


class SimulationBase(BaseModel):
    """Schéma de base pour les simulations"""
    patient_id: int = Field(..., description="ID du patient")
    intervention_type: str = Field(..., description="Type d'intervention")
    dose: float = Field(..., description="Dosage de l'intervention")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Paramètres spécifiques")

    @validator('intervention_type')
    def validate_intervention_type(cls, v):
        """Valider le type d'intervention"""
        if v not in INTERVENTION_TYPES:
            valid_types = list(INTERVENTION_TYPES.keys())
            raise ValueError(f'Type d\'intervention non valide. Types disponibles: {valid_types}')
        return v

    @validator('dose')
    def validate_dose(cls, v, values):
        """Valider le dosage selon le type d'intervention"""
        if 'intervention_type' in values:
            intervention = INTERVENTION_TYPES.get(values['intervention_type'])
            if intervention:
                min_dose = intervention['min_dose']
                max_dose = intervention['max_dose']
                if not (min_dose <= v <= max_dose):
                    unit = intervention['unit']
                    raise ValueError(
                        f'Dosage non valide pour {intervention["name"]}. '
                        f'Doit être entre {min_dose} et {max_dose} {unit}'
                    )
        return v


class SimulationCreate(SimulationBase):
    """Schéma pour créer une simulation"""
    pass


class SimulationUpdate(BaseModel):
    """Schéma pour mettre à jour une simulation"""
    status: Optional[str] = None
    generated_image_path: Optional[str] = None
    model_version: Optional[str] = None
    generation_time: Optional[float] = None

    @validator('status')
    def validate_status(cls, v):
        """Valider le statut"""
        if v is not None:
            valid_statuses = ['pending', 'processing', 'completed', 'failed']
            if v not in valid_statuses:
                raise ValueError(f'Statut non valide. Statuts autorisés: {valid_statuses}')
        return v


class SimulationResponse(SimulationBase):
    """Schéma de réponse pour les simulations"""
    id: int
    user_id: int
    original_image_path: str
    generated_image_path: Optional[str] = None
    model_version: Optional[str] = None
    generation_time: Optional[float] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SimulationSummary(BaseModel):
    """Schéma résumé pour les listes de simulations"""
    id: int
    patient_id: int
    intervention_type: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class SimulationStats(BaseModel):
    """Schémas pour les statistiques de simulations"""
    total_simulations: int
    completed_simulations: int
    failed_simulations: int
    average_generation_time: Optional[float] = None
    most_common_intervention: Optional[str] = None


class InterventionTypeInfo(BaseModel):
    """Schéma pour les informations sur un type d'intervention"""
    name: str
    min_dose: float
    max_dose: float
    unit: str
    description: str


class AvailableInterventions(BaseModel):
    """Schéma pour la liste des interventions disponibles"""
    interventions: Dict[str, InterventionTypeInfo]
