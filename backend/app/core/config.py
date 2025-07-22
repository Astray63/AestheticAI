"""
Configuration centrale de l'application AestheticAI
Gestion des paramètres d'environnement et configuration par environnement
"""

import os
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseSettings


class Settings(BaseSettings):
    """Configuration de l'application avec validation Pydantic"""
    
    # === Configuration de base ===
    app_name: str = "AestheticAI"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # === Chemins et répertoires ===
    base_dir: Path = Path(__file__).parent.parent
    upload_dir: Path = base_dir / "uploads"
    models_dir: Path = base_dir / "models"
    
    # === Base de données ===
    database_url: str = "sqlite:///./aesthetic_app.db"
    
    # === Sécurité ===
    secret_key: str = "changez-moi-en-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # === Configuration IA ===
    use_gpu: bool = False
    device: str = "cpu"
    model_name: str = "runwayml/stable-diffusion-v1-5"
    controlnet_model: str = "lllyasviel/sd-controlnet-canny"
    
    # === Paramètres de génération ===
    max_image_size: int = 1024
    inference_steps: int = 20
    guidance_scale: float = 7.5
    max_inference_time: int = 120
    
    # === API Configuration ===
    cors_origins: list = ["http://localhost:3000", "http://localhost:5173"]
    max_upload_size: int = 50 * 1024 * 1024  # 50MB
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Créer les dossiers s'ils n'existent pas
        self.upload_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
        # Configuration automatique du device
        if self.use_gpu:
            try:
                import torch
                self.device = "cuda" if torch.cuda.is_available() else "cpu"
            except ImportError:
                self.device = "cpu"


# Types d'interventions supportées
INTERVENTION_TYPES: Dict[str, Dict[str, Any]] = {
    "lips": {
        "name": "Lèvres",
        "min_dose": 0.5,
        "max_dose": 5.0,
        "unit": "ml",
        "description": "Augmentation et redefinition des lèvres"
    },
    "cheeks": {
        "name": "Pommettes",
        "min_dose": 1.0,
        "max_dose": 8.0,
        "unit": "ml",
        "description": "Redéfinition des pommettes"
    },
    "chin": {
        "name": "Menton",
        "min_dose": 1.0,
        "max_dose": 6.0,
        "unit": "ml",
        "description": "Remodelage du menton"
    },
    "forehead": {
        "name": "Front",
        "min_dose": 10,
        "max_dose": 50,
        "unit": "unités",
        "description": "Traitement des rides du front"
    },
    "crow_feet": {
        "name": "Pattes d'oie",
        "min_dose": 5,
        "max_dose": 25,
        "unit": "unités",
        "description": "Traitement des rides de la patte d'oie"
    }
}

# Instance globale des settings
settings = Settings()
