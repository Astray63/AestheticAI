"""
Application principale AestheticAI
Point d'entrée FastAPI modernisé avec architecture modulaire
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import create_tables
from app.services.ai_generator import ai_service
from app.api import auth_router, patients_router, simulations_router, main_router

# Configuration du logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestionnaire de cycle de vie de l'application"""
    # Startup
    logger.info(f"Démarrage de {settings.app_name} v{settings.app_version}")
    logger.info(f"Environnement: {settings.environment}")
    logger.info(f"Device IA: {settings.device}")
    
    # Créer les tables de base de données
    create_tables()
    logger.info("Tables de base de données créées")
    
    # Initialiser les modèles IA en arrière-plan
    try:
        await ai_service.initialize_models()
        logger.info("Modèles IA initialisés")
    except Exception as e:
        logger.warning(f"Erreur lors de l'initialisation IA: {e}")
    
    yield
    
    # Shutdown
    logger.info("Arrêt de l'application")
    await ai_service.cleanup()


# Créer l'application FastAPI
app = FastAPI(
    title=settings.app_name,
    description="""
    🌟 **AestheticAI** - Plateforme SaaS de Médecine Esthétique avec IA

    API moderne pour la simulation d'interventions esthétiques utilisant
    l'intelligence artificielle générative (Stable Diffusion + ControlNet).

    ## Fonctionnalités

    * 🔐 **Authentification sécurisée** avec codes PIN et JWT
    * 👥 **Gestion des patients** anonymisée (conforme RGPD)
    * 🤖 **Simulations IA** pour visualiser les résultats avant intervention
    * 📊 **Statistiques et suivi** des interventions
    * 🏥 **Interface professionnelle** dédiée aux professionnels de santé

    ## Types d'interventions supportées

    * Augmentation des lèvres
    * Redéfinition des pommettes
    * Remodelage du menton
    * Traitement des rides (front, pattes d'oie)

    ## Sécurité

    * Authentification JWT avec codes PIN
    * Données patients anonymisées
    * Conformité RGPD
    * Chiffrement des données sensibles
    """,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers uploadés
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Inclure les routers
app.include_router(main_router)
app.include_router(auth_router, prefix="/api")
app.include_router(patients_router, prefix="/api")
app.include_router(simulations_router, prefix="/api")

# Router pour les abonnements (à importer depuis l'ancien code si nécessaire)
try:
    from subscription_api import router as subscription_router
    app.include_router(subscription_router, prefix="/api")
    logger.info("Router d'abonnements inclus")
except ImportError:
    logger.warning("Router d'abonnements non trouvé")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info" if not settings.debug else "debug"
    )
