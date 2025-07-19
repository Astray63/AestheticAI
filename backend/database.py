from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """Utilisateur professionnel de santé"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_pin = Column(String)
    full_name = Column(String)
    speciality = Column(String)
    license_number = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Patient(Base):
    """Données patient anonymisées"""

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    anonymous_id = Column(String, unique=True, default=lambda: str(uuid.uuid4()))
    age_range = Column(String)  # "25-30", "31-40", etc.
    gender = Column(String)
    skin_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Simulation(Base):
    """Simulation d'intervention esthétique"""

    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer)
    user_id = Column(Integer)

    # Images
    original_image_path = Column(String)
    generated_image_path = Column(String)

    # Intervention
    intervention_type = Column(String)  # lips, cheeks, chin, etc.
    dose = Column(Float)
    parameters = Column(Text)  # JSON des paramètres spécifiques

    # Métadonnées IA
    model_version = Column(String)
    generation_time = Column(Float)  # en secondes

    # Statut
    status = Column(String, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


def create_tables():
    """Créer toutes les tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dépendance pour obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
