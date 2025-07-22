"""
Schémas Pydantic pour les utilisateurs (professionnels de santé)
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs"""
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur unique")
    full_name: str = Field(..., min_length=2, max_length=100, description="Nom complet du professionnel")
    speciality: str = Field(..., description="Spécialité médicale")
    license_number: str = Field(..., description="Numéro de licence professionnelle")

    @validator('username')
    def validate_username(cls, v):
        """Valider le nom d'utilisateur"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Le nom d\'utilisateur ne peut contenir que des lettres, chiffres, tirets et underscores')
        return v.lower()

    @validator('speciality')
    def validate_speciality(cls, v):
        """Valider la spécialité"""
        valid_specialities = [
            'medecine_esthetique', 'chirurgie_plastique', 'dermatologie',
            'chirurgie_maxillo_faciale', 'autre'
        ]
        if v not in valid_specialities:
            raise ValueError(f'Spécialité non reconnue. Valeurs autorisées: {valid_specialities}')
        return v


class UserCreate(UserBase):
    """Schéma pour créer un utilisateur"""
    pin: str = Field(..., min_length=4, max_length=8, description="Code PIN pour l'authentification")

    @validator('pin')
    def validate_pin(cls, v):
        """Valider le PIN"""
        if not v.isdigit():
            raise ValueError('Le PIN ne peut contenir que des chiffres')
        if len(v) < 4:
            raise ValueError('Le PIN doit contenir au moins 4 chiffres')
        return v


class UserUpdate(BaseModel):
    """Schéma pour mettre à jour un utilisateur"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    speciality: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schéma de réponse pour les utilisateurs"""
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schéma pour la connexion"""
    username: str = Field(..., description="Nom d'utilisateur")
    pin: str = Field(..., description="Code PIN")


class TokenResponse(BaseModel):
    """Schéma de réponse pour les tokens JWT"""
    access_token: str = Field(..., description="Token d'accès JWT")
    token_type: str = Field(default="bearer", description="Type de token")
    expires_in: int = Field(..., description="Durée de validité en secondes")
