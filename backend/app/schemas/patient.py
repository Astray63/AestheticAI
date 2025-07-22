"""
Schémas Pydantic pour les patients
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class PatientBase(BaseModel):
    """Schéma de base pour les patients"""
    age_range: str = Field(..., description="Tranche d'âge du patient")
    gender: str = Field(..., description="Genre du patient")
    skin_type: str = Field(..., description="Type de peau")

    @validator('age_range')
    def validate_age_range(cls, v):
        """Valider la tranche d'âge"""
        valid_ranges = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']
        if v not in valid_ranges:
            raise ValueError(f'Tranche d\'âge non valide. Valeurs autorisées: {valid_ranges}')
        return v

    @validator('gender')
    def validate_gender(cls, v):
        """Valider le genre"""
        valid_genders = ['M', 'F', 'Autre']
        if v not in valid_genders:
            raise ValueError(f'Genre non valide. Valeurs autorisées: {valid_genders}')
        return v

    @validator('skin_type')
    def validate_skin_type(cls, v):
        """Valider le type de peau"""
        valid_types = ['Claire', 'Mate', 'Foncée', 'Mixte']
        if v not in valid_types:
            raise ValueError(f'Type de peau non valide. Valeurs autorisées: {valid_types}')
        return v


class PatientCreate(PatientBase):
    """Schéma pour créer un patient"""
    pass


class PatientUpdate(BaseModel):
    """Schéma pour mettre à jour un patient"""
    age_range: Optional[str] = None
    gender: Optional[str] = None
    skin_type: Optional[str] = None


class PatientResponse(PatientBase):
    """Schéma de réponse pour les patients"""
    id: int
    anonymous_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class PatientSummary(BaseModel):
    """Schéma résumé pour les listes de patients"""
    id: int
    anonymous_id: str
    age_range: str
    gender: str
    created_at: datetime

    class Config:
        from_attributes = True
