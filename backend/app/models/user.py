"""
Modèle User - Professionnel de santé
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """
    Modèle représentant un professionnel de santé utilisant l'application
    
    Attributes:
        id: Identifiant unique
        username: Nom d'utilisateur unique
        hashed_pin: PIN hashé pour l'authentification
        full_name: Nom complet du professionnel
        speciality: Spécialité médicale
        license_number: Numéro de licence professionnelle
        is_active: Statut actif du compte
        created_at: Date de création du compte
    """
    
    __tablename__ = "users"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentification
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_pin = Column(String, nullable=False)
    
    # Informations professionnelles
    full_name = Column(String, nullable=False)
    speciality = Column(String, nullable=False)
    license_number = Column(String, unique=True, nullable=False)
    
    # Statut et métadonnées
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', speciality='{self.speciality}')>"
