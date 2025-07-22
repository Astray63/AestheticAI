"""
Modèle Simulation - Simulation d'intervention esthétique
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
import json

from app.core.database import Base


class Simulation(Base):
    """
    Modèle représentant une simulation d'intervention esthétique
    
    Attributes:
        id: Identifiant unique
        patient_id: Référence vers le patient
        user_id: Référence vers le professionnel
        original_image_path: Chemin vers l'image originale
        generated_image_path: Chemin vers l'image générée
        intervention_type: Type d'intervention
        dose: Dosage/quantité de l'intervention
        parameters: Paramètres JSON de l'intervention
        model_version: Version du modèle IA utilisé
        generation_time: Temps de génération en secondes
        status: Statut de la simulation
        created_at: Date de création
        completed_at: Date de completion
    """
    
    __tablename__ = "simulations"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True)
    
    # Relations
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Images
    original_image_path = Column(String, nullable=False)
    generated_image_path = Column(String, nullable=True)
    
    # Intervention
    intervention_type = Column(String, nullable=False)  # lips, cheeks, chin, etc.
    dose = Column(Float, nullable=False)
    parameters = Column(Text, nullable=True)  # JSON des paramètres spécifiques
    
    # Métadonnées IA
    model_version = Column(String, nullable=True)
    generation_time = Column(Float, nullable=True)  # en secondes
    
    # Statut et tracking
    status = Column(String, default="pending", nullable=False)  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    def get_parameters(self) -> Dict[str, Any]:
        """Désérialiser les paramètres JSON"""
        if self.parameters:
            try:
                return json.loads(self.parameters)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_parameters(self, params: Dict[str, Any]) -> None:
        """Sérialiser les paramètres en JSON"""
        self.parameters = json.dumps(params) if params else None
    
    def mark_completed(self, generation_time: float) -> None:
        """Marquer la simulation comme terminée"""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
        self.generation_time = generation_time
    
    def mark_failed(self) -> None:
        """Marquer la simulation comme échouée"""
        self.status = "failed"
        self.completed_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"<Simulation(id={self.id}, type='{self.intervention_type}', status='{self.status}')>"
