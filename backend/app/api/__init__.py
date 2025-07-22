"""APIs de l'application AestheticAI"""

from .auth import router as auth_router
from .patients import router as patients_router
from .simulations import router as simulations_router
from .main import router as main_router

__all__ = ["auth_router", "patients_router", "simulations_router", "main_router"]
