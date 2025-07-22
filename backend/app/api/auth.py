"""API endpoints pour l'authentification"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth import auth_service, get_current_user
from app.schemas import (
    UserCreate, UserResponse, UserLogin, TokenResponse,
    SuccessResponse
)
from app.models import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Enregistrer un nouveau professionnel de santé
    
    Crée un compte pour un professionnel de santé avec validation
    des informations professionnelles.
    """
    try:
        user = auth_service.create_user(db, user_data)
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la création du compte: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Connecter un utilisateur avec nom d'utilisateur et PIN
    
    Retourne un token JWT valide pour l'authentification
    des requêtes suivantes.
    """
    try:
        return auth_service.login(db, login_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors de la connexion: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Obtenir les informations de l'utilisateur connecté
    
    Retourne les informations du profil de l'utilisateur
    actuellement authentifié.
    """
    return UserResponse.from_orm(current_user)


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Déconnecter l'utilisateur
    
    Note: Avec JWT, la déconnexion est gérée côté client
    en supprimant le token. Cette endpoint confirme la déconnexion.
    """
    return SuccessResponse(
        message=f"Utilisateur {current_user.username} déconnecté avec succès"
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_user)
):
    """
    Renouveler le token d'authentification
    
    Génère un nouveau token pour l'utilisateur connecté
    pour prolonger sa session.
    """
    try:
        access_token = auth_service.create_access_token(
            data={"sub": current_user.username, "user_id": current_user.id}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=30 * 60  # 30 minutes
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur lors du renouvellement du token: {str(e)}"
        )
