"""API endpoints pour les simulations d'interventions esthétiques"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
import asyncio
from pathlib import Path
from PIL import Image
import io

from app.core.database import get_db
from app.core.config import settings
from app.services.auth import get_current_user
from app.services.ai_generator import ai_service
from app.schemas import (
    SimulationResponse, SimulationSummary, SimulationCreate,
    SimulationStats, AvailableInterventions, InterventionTypeInfo,
    SuccessResponse
)
from app.models import User, Patient, Simulation

router = APIRouter(prefix="/simulations", tags=["Simulations"])


@router.get("/interventions", response_model=AvailableInterventions)
async def get_available_interventions():
    """
    Obtenir la liste des interventions disponibles
    
    Retourne tous les types d'interventions supportés
    avec leurs paramètres (doses min/max, unités, etc.).
    """
    try:
        interventions_data = await ai_service.get_available_interventions()
        
        # Convertir en format de réponse
        interventions = {}
        for key, value in interventions_data.items():
            interventions[key] = InterventionTypeInfo(**value)
        
        return AvailableInterventions(interventions=interventions)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des interventions: {str(e)}"
        )


@router.post("/", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def create_simulation(
    patient_id: int = Form(...),
    intervention_type: str = Form(...),
    dose: float = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Créer une nouvelle simulation d'intervention
    
    Lance le processus de génération d'image avec IA
    pour simuler le résultat d'une intervention esthétique.
    """
    # Vérifier que le patient existe
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    # Valider les paramètres d'intervention
    is_valid, error_msg = ai_service.validate_intervention_parameters(
        intervention_type, dose
    )
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Valider le fichier image
    if not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le fichier doit être une image"
        )
    
    try:
        # Lire et traiter l'image
        image_content = await image.read()
        original_image = Image.open(io.BytesIO(image_content))
        
        # Générer un nom de fichier unique
        file_id = str(uuid.uuid4())
        original_filename = f"{file_id}_original.jpg"
        generated_filename = f"{file_id}_generated.jpg"
        
        # Sauvegarder l'image originale
        original_path = settings.upload_dir / original_filename
        original_image.save(original_path, "JPEG", quality=90)
        
        # Créer l'entrée en base de données
        db_simulation = Simulation(
            patient_id=patient_id,
            user_id=current_user.id,
            original_image_path=str(original_path),
            intervention_type=intervention_type,
            dose=dose,
            status="processing"
        )
        
        db.add(db_simulation)
        db.commit()
        db.refresh(db_simulation)
        
        # Lancer la génération en arrière-plan
        asyncio.create_task(
            process_simulation(db_simulation.id, original_image, intervention_type, dose)
        )
        
        return SimulationResponse.from_orm(db_simulation)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création de la simulation: {str(e)}"
        )


async def process_simulation(
    simulation_id: int,
    original_image: Image.Image,
    intervention_type: str,
    dose: float
):
    """
    Traiter une simulation en arrière-plan
    
    Args:
        simulation_id: ID de la simulation
        original_image: Image originale PIL
        intervention_type: Type d'intervention
        dose: Dosage de l'intervention
    """
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        if not simulation:
            return
        
        # Générer l'image avec l'IA
        generated_image, metadata = await ai_service.generate_simulation(
            original_image, intervention_type, dose
        )
        
        # Sauvegarder l'image générée
        file_id = Path(simulation.original_image_path).stem.split('_')[0]
        generated_filename = f"{file_id}_generated.jpg"
        generated_path = settings.upload_dir / generated_filename
        generated_image.save(generated_path, "JPEG", quality=90)
        
        # Mettre à jour la simulation
        simulation.generated_image_path = str(generated_path)
        simulation.model_version = metadata.get("model_version")
        simulation.generation_time = metadata.get("generation_time")
        simulation.mark_completed(metadata.get("generation_time", 0))
        
        db.commit()
        
    except Exception as e:
        # Marquer comme échouée en cas d'erreur
        if simulation:
            simulation.mark_failed()
            db.commit()
        print(f"Erreur lors du traitement de la simulation {simulation_id}: {e}")
    finally:
        db.close()


@router.get("/", response_model=List[SimulationSummary])
async def list_simulations(
    skip: int = 0,
    limit: int = 50,
    patient_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lister les simulations avec filtres et pagination
    
    Retourne une liste paginée des simulations avec
    possibilité de filtrer par patient et statut.
    """
    try:
        query = db.query(Simulation).filter(Simulation.user_id == current_user.id)
        
        if patient_id:
            query = query.filter(Simulation.patient_id == patient_id)
        
        if status:
            query = query.filter(Simulation.status == status)
        
        simulations = query.offset(skip).limit(limit).all()
        
        return [SimulationSummary.from_orm(sim) for sim in simulations]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des simulations: {str(e)}"
        )


@router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtenir les détails d'une simulation spécifique
    
    Retourne toutes les informations d'une simulation
    incluant les chemins des images et métadonnées.
    """
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation non trouvée"
        )
    
    return SimulationResponse.from_orm(simulation)


@router.delete("/{simulation_id}", response_model=SuccessResponse)
async def delete_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprimer une simulation et ses fichiers associés
    
    Supprime la simulation de la base de données et
    nettoie les fichiers images associés.
    """
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id,
        Simulation.user_id == current_user.id
    ).first()
    
    if not simulation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation non trouvée"
        )
    
    try:
        # Supprimer les fichiers images
        if simulation.original_image_path:
            Path(simulation.original_image_path).unlink(missing_ok=True)
        if simulation.generated_image_path:
            Path(simulation.generated_image_path).unlink(missing_ok=True)
        
        # Supprimer de la base de données
        db.delete(simulation)
        db.commit()
        
        return SuccessResponse(
            message=f"Simulation {simulation_id} supprimée avec succès"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )


@router.get("/stats/user", response_model=SimulationStats)
async def get_user_simulation_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtenir les statistiques de simulations de l'utilisateur
    
    Retourne un résumé des simulations effectuées par
    l'utilisateur connecté.
    """
    try:
        simulations = db.query(Simulation).filter(
            Simulation.user_id == current_user.id
        ).all()
        
        total = len(simulations)
        completed = len([s for s in simulations if s.status == "completed"])
        failed = len([s for s in simulations if s.status == "failed"])
        
        # Calculer le temps moyen de génération
        completed_sims = [s for s in simulations if s.generation_time]
        avg_time = None
        if completed_sims:
            avg_time = sum(s.generation_time for s in completed_sims) / len(completed_sims)
        
        # Intervention la plus courante
        from collections import Counter
        intervention_counts = Counter(s.intervention_type for s in simulations)
        most_common = intervention_counts.most_common(1)
        most_common_intervention = most_common[0][0] if most_common else None
        
        return SimulationStats(
            total_simulations=total,
            completed_simulations=completed,
            failed_simulations=failed,
            average_generation_time=avg_time,
            most_common_intervention=most_common_intervention
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du calcul des statistiques: {str(e)}"
        )
