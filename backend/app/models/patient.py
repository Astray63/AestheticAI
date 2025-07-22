"""
Modèle Patient - Données patient anonymisées
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


class Patient(Base):
    """
    Modèle représentant un patient de manière anonymisée
    
    Respecte le RGPD en stockant uniquement des données non identifiantes
    
    Attributes:
        id: Identifiant unique interne
        anonymous_id: Identifiant anonyme externe
        age_range: Tranche d'âge du patient
        gender: Genre du patient
        skin_type: Type de peau pour l'IA
        created_at: Date de création du dossier
    """
    
    __tablename__ = "patients"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)
    
    # Identifiant anonyme pour l'externe
    anonymous_id = Column(
        String, 
        unique=True, 
        default=lambda: str(uuid.uuid4()), 
        nullable=False
    )
    
    # Données démographiques anonymisées
    age_range = Column(String, nullable=False)  # "18-25", "26-35", etc.
    gender = Column(String, nullable=False)     # "M", "F", "Autre"
    skin_type = Column(String, nullable=False)  # "Claire", "Mate", "Foncée"
    
    # Métadonnées
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<Patient(id={self.id}, age_range='{self.age_range}', skin_type='{self.skin_type}')>"
