"""
Configuration de base de données modernisée
Utilise SQLAlchemy 2.0 avec une approche modulaire
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

# Configuration de l'engine avec les bonnes options
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.debug,  # Log SQL en mode debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class pour les modèles
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dépendance FastAPI pour obtenir une session de base de données
    Utilise un context manager pour garantir la fermeture
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    """Créer toutes les tables définies dans les modèles"""
    Base.metadata.create_all(bind=engine)


def drop_tables() -> None:
    """Supprimer toutes les tables (pour les tests)"""
    Base.metadata.drop_all(bind=engine)
