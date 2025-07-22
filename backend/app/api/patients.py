"""API endpoints pour la gestion des patients"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.services.auth import get_current_user
from app.schemas import (
    PatientCreate, PatientResponse, PatientSummary, PatientUpdate,
    SuccessResponse, PaginatedResponse
)
from app.models import User, Patient

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Créer un nouveau dossier patient anonymisé
    
    Crée un dossier patient avec des données anonymisées
    conformes au RGPD.
    """
    try:
        db_patient = Patient(**patient_data.dict())
        db.add(db_patient)
        db.commit()
        db.refresh(db_patient)
        
        return PatientResponse.from_orm(db_patient)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du patient: {str(e)}"
        )


@router.get("/", response_model=List[PatientSummary])
async def list_patients(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lister les patients avec pagination
    
    Retourne une liste paginée des patients avec
    leurs informations de base.
    """
    try:
        patients = db.query(Patient).offset(skip).limit(limit).all()
        return [PatientSummary.from_orm(patient) for patient in patients]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la récupération des patients: {str(e)}"
        )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtenir les détails d'un patient spécifique
    
    Retourne toutes les informations disponibles
    pour un patient donné.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    return PatientResponse.from_orm(patient)


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mettre à jour les informations d'un patient
    
    Met à jour les informations modifiables du patient
    (exclut l'ID anonyme pour la traçabilité).
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    try:
        update_data = patient_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(patient, field, value)
        
        db.commit()
        db.refresh(patient)
        
        return PatientResponse.from_orm(patient)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la mise à jour: {str(e)}"
        )


@router.delete("/{patient_id}", response_model=SuccessResponse)
async def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Supprimer un patient (soft delete ou anonymisation renforcée)
    
    Note: En production, il faudrait implémenter une suppression
    conforme au RGPD avec anonymisation des données liées.
    """
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    try:
        # TODO: Implémenter une suppression conforme RGPD
        # Pour l'instant, suppression simple
        db.delete(patient)
        db.commit()
        
        return SuccessResponse(
            message=f"Patient {patient.anonymous_id} supprimé avec succès"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la suppression: {str(e)}"
        )


@router.get("/search/by-anonymous-id/{anonymous_id}", response_model=PatientResponse)
async def get_patient_by_anonymous_id(
    anonymous_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rechercher un patient par son ID anonyme
    
    Permet de retrouver un patient en utilisant
    son identifiant anonymisé externe.
    """
    patient = db.query(Patient).filter(Patient.anonymous_id == anonymous_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé avec cet ID anonyme"
        )
    
    return PatientResponse.from_orm(patient)
