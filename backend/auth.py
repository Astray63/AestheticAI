from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt  # PyJWT
from passlib.context import CryptContext
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Configuration pour le hachage des PINs
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_pin(pin: str) -> str:
    """Hacher un PIN"""
    return pwd_context.hash(pin)


def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """Vérifier un PIN"""
    return pwd_context.verify(plain_pin, hashed_pin)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Créer un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Vérifier un token JWT et retourner le payload"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token invalide")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Obtenir l'utilisateur actuel à partir du token"""
    payload = verify_token(credentials.credentials)
    return payload.get("sub")


def get_current_user_from_token(token: str, db=None) -> str:
    """Obtenir l'utilisateur actuel à partir d'un token (pour les tests)"""
    payload = verify_token(token)
    return payload.get("sub")


def get_current_user_object(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Obtenir l'objet User complet à partir du token"""
    from database import User, get_db  # Import local pour éviter les dépendances circulaires
    from sqlalchemy.orm import Session
    
    # Obtenir la session DB
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        payload = verify_token(credentials.credentials)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
        return user
    finally:
        db.close()
