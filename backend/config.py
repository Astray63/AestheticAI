import os
from pathlib import Path

# Configuration de base
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploads"
MODELS_DIR = BASE_DIR / "models"

# Créer les dossiers s'ils n'existent pas
UPLOAD_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# Base de données
DATABASE_URL = "sqlite:///./aesthetic_app.db"

# Sécurité
SECRET_KEY = os.getenv("SECRET_KEY", "votre-cle-secrete-super-forte-ici")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration IA
DEVICE = "cuda" if os.getenv("USE_GPU", "false").lower() == "true" else "cpu"
MODEL_NAME = "runwayml/stable-diffusion-v1-5"
CONTROLNET_MODEL = "lllyasviel/sd-controlnet-canny"

# Paramètres de génération
MAX_IMAGE_SIZE = 1024
INFERENCE_STEPS = 20
GUIDANCE_SCALE = 7.5

# Types d'interventions supportées
INTERVENTION_TYPES = {
    "lips": {"name": "Lèvres", "min_dose": 0.5, "max_dose": 5.0, "unit": "ml"},
    "cheeks": {"name": "Pommettes", "min_dose": 1.0, "max_dose": 8.0, "unit": "ml"},
    "chin": {"name": "Menton", "min_dose": 1.0, "max_dose": 6.0, "unit": "ml"},
    "forehead": {"name": "Front", "min_dose": 10, "max_dose": 50, "unit": "unités"},
}
