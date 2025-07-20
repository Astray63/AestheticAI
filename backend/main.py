from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import uuid
import shutil
from pathlib import Path
import logging
import asyncio
from datetime import datetime

from database import get_db, create_tables, User, Patient, Simulation
from schemas import *
from config import INTERVENTION_TYPES, UPLOAD_DIR
from ai_generator import ai_generator
from auth import create_access_token, verify_token, hash_pin, verify_pin
from subscription_api import router as subscription_router

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aesthetic Medicine AI Simulator",
    description="Application de simulation d'interventions esthétiques avec IA générative",
    version="1.0.0",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers uploadés
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# Inclure les routers
app.include_router(subscription_router)

# Sécurité
security = HTTPBearer()


@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    logger.info("Démarrage de l'application...")

    # Créer les tables de base de données
    create_tables()

    # Initialiser les modèles IA
    await ai_generator.initialize()

    logger.info("Application prête !")


@app.get("/")
async def root():
    """Point d'entrée de l'API"""
    return {
        "message": "Aesthetic Medicine AI Simulator API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Vérification de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "ai_ready": ai_generator.pipeline is not None,
    }


@app.get("/version")
async def get_version():
    """Obtenir la version de l'API"""
    return {
        "version": "1.0.0",
        "api_name": "AestheticAI",
        "description": "API pour simulations d'interventions esthétiques",
        "python_version": "3.11+",
    }


# === AUTHENTIFICATION ===


@app.post("/auth/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Enregistrer un nouveau professionnel de santé"""

    # Vérifier si l'utilisateur existe déjà
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà utilisé")

    # Créer le nouvel utilisateur
    hashed_pin = hash_pin(user_data.pin)
    db_user = User(
        username=user_data.username,
        hashed_pin=hashed_pin,
        full_name=user_data.full_name,
        speciality=user_data.speciality,
        license_number=user_data.license_number,
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


@app.post("/auth/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Connexion avec PIN"""

    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_pin(login_data.pin, user.hashed_pin):
        raise HTTPException(status_code=401, detail="Identifiants incorrects")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Compte désactivé")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Obtenir l'utilisateur connecté"""
    username = verify_token(credentials.credentials)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    return user


# === GESTION DES PATIENTS ===


@app.post("/patients", response_model=PatientResponse)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Créer un nouveau dossier patient (anonymisé)"""

    db_patient = Patient(
        age_range=patient_data.age_range,
        gender=patient_data.gender,
        skin_type=patient_data.skin_type,
    )

    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)

    return db_patient


@app.get("/patients", response_model=list[PatientResponse])
async def list_patients(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Lister les patients"""
    patients = db.query(Patient).order_by(Patient.created_at.desc()).limit(50).all()
    return patients


# === INFORMATIONS SUR LES INTERVENTIONS ===


@app.get("/interventions", response_model=Dict[str, InterventionInfo])
async def get_intervention_types():
    """Obtenir les types d'interventions disponibles"""
    return INTERVENTION_TYPES


# === SIMULATION IA ===


@app.post("/simulations", response_model=SimulationResponse)
async def create_simulation(
    patient_id: int = Form(...),
    intervention_type: str = Form(...),
    dose: float = Form(...),
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Créer une nouvelle simulation d'intervention"""

    # Vérifier que le patient existe
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient non trouvé")

    # Vérifier le type d'intervention
    if intervention_type not in INTERVENTION_TYPES:
        raise HTTPException(status_code=400, detail="Type d'intervention non supporté")

    # Vérifier la dose
    intervention_info = INTERVENTION_TYPES[intervention_type]
    if not (intervention_info["min_dose"] <= dose <= intervention_info["max_dose"]):
        raise HTTPException(
            status_code=400,
            detail=f"Dose invalide. Range: {intervention_info['min_dose']}-{intervention_info['max_dose']} {intervention_info['unit']}",
        )

    # Vérifier le type de fichier
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Le fichier doit être une image")

    # Sauvegarder l'image originale
    image_id = str(uuid.uuid4())
    original_filename = f"original_{image_id}_{image.filename}"
    original_path = UPLOAD_DIR / original_filename

    with open(original_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Créer l'enregistrement de simulation
    db_simulation = Simulation(
        patient_id=patient_id,
        user_id=current_user.id,
        original_image_path=str(original_path),
        intervention_type=intervention_type,
        dose=dose,
        status="processing",
    )

    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)

    # Lancer la génération IA en arrière-plan
    asyncio.create_task(
        process_simulation(
            db_simulation.id, str(original_path), intervention_type, dose
        )
    )

    return db_simulation


async def process_simulation(
    simulation_id: int, image_path: str, intervention_type: str, dose: float
):
    """Traiter la simulation IA en arrière-plan"""

    # Obtenir une nouvelle session DB pour cette tâche
    from database import SessionLocal

    db = SessionLocal()

    try:
        # Récupérer la simulation
        simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not simulation:
            return

        # Générer l'image avec l'IA
        generated_path, generation_time = (
            await ai_generator.generate_aesthetic_simulation(
                image_path, intervention_type, dose
            )
        )

        # Mettre à jour la simulation
        simulation.generated_image_path = generated_path
        simulation.generation_time = generation_time
        simulation.status = "completed"
        simulation.completed_at = datetime.utcnow()

        db.commit()
        logger.info(f"Simulation {simulation_id} terminée en {generation_time:.2f}s")

    except Exception as e:
        logger.error(f"Erreur lors du traitement de la simulation {simulation_id}: {e}")

        # Marquer comme échouée
        simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if simulation:
            simulation.status = "failed"
            db.commit()

    finally:
        db.close()


@app.get("/simulations/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(
    simulation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Obtenir une simulation par ID"""

    simulation = (
        db.query(Simulation)
        .filter(Simulation.id == simulation_id, Simulation.user_id == current_user.id)
        .first()
    )

    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation non trouvée")

    return simulation


@app.get("/simulations", response_model=list[SimulationResponse])
async def list_simulations(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Lister les simulations de l'utilisateur"""

    simulations = (
        db.query(Simulation)
        .filter(Simulation.user_id == current_user.id)
        .order_by(Simulation.created_at.desc())
        .limit(50)
        .all()
    )

    return simulations


@app.get("/images/{filename}")
async def get_image(filename: str, current_user: User = Depends(get_current_user)):
    """Servir une image de manière sécurisée"""

    file_path = UPLOAD_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image non trouvée")

    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
