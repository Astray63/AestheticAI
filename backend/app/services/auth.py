"""
Service d'authentification pour AestheticAI
Gestion des utilisateurs, authentification JWT et sécurité
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, TokenResponse


class AuthService:
    """Service pour gérer l'authentification et la sécurité"""
    
    def __init__(self):
        # Configuration pour le hachage des PINs
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.security = HTTPBearer()
    
    def hash_pin(self, pin: str) -> str:
        """Hacher un PIN avec bcrypt"""
        return self.pwd_context.hash(pin)
    
    def verify_pin(self, plain_pin: str, hashed_pin: str) -> bool:
        """Vérifier un PIN contre son hash"""
        return self.pwd_context.verify(plain_pin, hashed_pin)
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Créer un token JWT
        
        Args:
            data: Données à encoder dans le token
            expires_delta: Durée de validité personnalisée
            
        Returns:
            Token JWT encodé
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=settings.access_token_expire_minutes
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": settings.app_name
        })
        
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.secret_key, 
            algorithm=settings.algorithm
        )
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Vérifier un token JWT et retourner le payload
        
        Args:
            token: Token JWT à vérifier
            
        Returns:
            Payload du token
            
        Raises:
            HTTPException: Si le token est invalide
        """
        try:
            payload = jwt.decode(
                token, 
                settings.secret_key, 
                algorithms=[settings.algorithm]
            )
            username: str = payload.get("sub")
            if username is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token invalide - utilisateur manquant"
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expiré"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalide"
            )
    
    def authenticate_user(self, db: Session, username: str, pin: str) -> Optional[User]:
        """
        Authentifier un utilisateur avec nom d'utilisateur et PIN
        
        Args:
            db: Session de base de données
            username: Nom d'utilisateur
            pin: PIN en clair
            
        Returns:
            Utilisateur authentifié ou None
        """
        user = db.query(User).filter(User.username == username.lower()).first()
        if not user:
            return None
        
        if not user.is_active:
            return None
            
        if not self.verify_pin(pin, user.hashed_pin):
            return None
            
        return user
    
    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """
        Créer un nouvel utilisateur
        
        Args:
            db: Session de base de données
            user_data: Données de l'utilisateur
            
        Returns:
            Utilisateur créé
            
        Raises:
            HTTPException: Si l'utilisateur existe déjà
        """
        # Vérifier si l'utilisateur existe déjà
        if db.query(User).filter(User.username == user_data.username.lower()).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nom d'utilisateur déjà utilisé"
            )
        
        if db.query(User).filter(User.license_number == user_data.license_number).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Numéro de licence déjà utilisé"
            )
        
        # Créer l'utilisateur
        hashed_pin = self.hash_pin(user_data.pin)
        db_user = User(
            username=user_data.username.lower(),
            hashed_pin=hashed_pin,
            full_name=user_data.full_name,
            speciality=user_data.speciality,
            license_number=user_data.license_number
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def login(self, db: Session, login_data: UserLogin) -> TokenResponse:
        """
        Connecter un utilisateur et générer un token
        
        Args:
            db: Session de base de données
            login_data: Données de connexion
            
        Returns:
            Token de réponse
            
        Raises:
            HTTPException: Si l'authentification échoue
        """
        user = self.authenticate_user(db, login_data.username, login_data.pin)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou PIN incorrect"
            )
        
        # Créer le token
        access_token = self.create_access_token(
            data={"sub": user.username, "user_id": user.id}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60
        )


# Instance globale du service d'authentification
auth_service = AuthService()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dépendance FastAPI pour obtenir l'utilisateur actuel
    
    Args:
        credentials: Credentials HTTP Bearer
        db: Session de base de données
        
    Returns:
        Utilisateur actuel
        
    Raises:
        HTTPException: Si l'authentification échoue
    """
    payload = auth_service.verify_token(credentials.credentials)
    username = payload.get("sub")
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Compte utilisateur désactivé"
        )
    
    return user


def get_current_user_from_token(token: str, db: Session) -> Optional[User]:
    """
    Obtenir l'utilisateur actuel à partir d'un token (pour les tests)
    
    Args:
        token: Token JWT
        db: Session de base de données
        
    Returns:
        Utilisateur ou None si le token est invalide
    """
    try:
        payload = auth_service.verify_token(token)
        username = payload.get("sub")
        return db.query(User).filter(User.username == username).first()
    except HTTPException:
        return None
