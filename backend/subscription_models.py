from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import enum

Base = declarative_base()

class SubscriptionTier(enum.Enum):
    """Niveaux d'abonnement"""
    FREEMIUM = "freemium"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class PaymentStatus(enum.Enum):
    """Statuts de paiement"""
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_pin = Column(String)
    full_name = Column(String)
    speciality = Column(String)
    license_number = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    clinic_name = Column(String)
    clinic_address = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relation avec l'abonnement
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    patients = relationship("Patient", back_populates="doctor")
    simulations = relationship("Simulation", back_populates="doctor")
    usage_stats = relationship("UsageStats", back_populates="user")

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREEMIUM)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    auto_renew = Column(Boolean, default=True)
    
    # Limites selon l'abonnement
    monthly_simulations_limit = Column(Integer, default=5)  # Freemium: 5
    storage_limit_mb = Column(Integer, default=100)  # Freemium: 100MB
    advanced_ai_features = Column(Boolean, default=False)
    priority_support = Column(Boolean, default=False)
    white_label = Column(Boolean, default=False)
    
    # Métadonnées
    stripe_subscription_id = Column(String)  # Pour intégration Stripe
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="subscription")
    payments = relationship("Payment", back_populates="subscription")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"))
    amount = Column(Float)  # Montant en euros
    currency = Column(String, default="EUR")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_date = Column(DateTime, default=datetime.utcnow)
    stripe_payment_id = Column(String)
    invoice_url = Column(String)
    
    # Relations
    subscription = relationship("Subscription", back_populates="payments")

class UsageStats(Base):
    __tablename__ = "usage_stats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    month = Column(Integer)  # Mois (1-12)
    year = Column(Integer)   # Année
    simulations_count = Column(Integer, default=0)
    storage_used_mb = Column(Float, default=0.0)
    ai_processing_time_seconds = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="usage_stats")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    anonymous_id = Column(String, unique=True, index=True)  # ID anonymisé RGPD
    age_range = Column(String)  # ex: "25-30", "40-45"
    gender = Column(String)
    skin_type = Column(String)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    doctor = relationship("User", back_populates="patients")
    simulations = relationship("Simulation", back_populates="patient")

class Simulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    
    # Données de simulation
    intervention_type = Column(String)
    dose = Column(Float)
    parameters = Column(Text)  # JSON des paramètres additionnels
    
    # Fichiers
    original_image_path = Column(String)
    generated_image_path = Column(String)
    
    # Métadonnées
    status = Column(String, default="pending")  # pending, processing, completed, failed
    generation_time = Column(Float)  # Temps de génération en secondes
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relations
    doctor = relationship("User", back_populates="simulations")
    patient = relationship("Patient", back_populates="simulations")

# Configuration de la base de données
DATABASE_URL = "sqlite:///./aesthetic_app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Créer toutes les tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_subscription_tiers():
    """Initialiser les niveaux d'abonnement par défaut"""
    db = SessionLocal()
    try:
        # Cette fonction pourrait être utilisée pour créer des tarifs par défaut
        pass
    finally:
        db.close()

# Utilitaires pour l'abonnement
def get_subscription_limits(tier: SubscriptionTier) -> dict:
    """Obtenir les limites selon le niveau d'abonnement"""
    limits = {
        SubscriptionTier.FREEMIUM: {
            "monthly_simulations": 5,
            "storage_mb": 100,
            "advanced_ai": False,
            "priority_support": False,
            "white_label": False,
            "price": 0
        },
        SubscriptionTier.STARTER: {
            "monthly_simulations": 50,
            "storage_mb": 1000,  # 1GB
            "advanced_ai": True,
            "priority_support": False,
            "white_label": False,
            "price": 29.99
        },
        SubscriptionTier.PROFESSIONAL: {
            "monthly_simulations": 200,
            "storage_mb": 5000,  # 5GB
            "advanced_ai": True,
            "priority_support": True,
            "white_label": False,
            "price": 99.99
        },
        SubscriptionTier.ENTERPRISE: {
            "monthly_simulations": -1,  # Illimité
            "storage_mb": -1,  # Illimité
            "advanced_ai": True,
            "priority_support": True,
            "white_label": True,
            "price": 299.99
        }
    }
    return limits.get(tier, limits[SubscriptionTier.FREEMIUM])

def check_usage_limits(user_id: int, db_session) -> dict:
    """Vérifier les limites d'utilisation pour un utilisateur"""
    from datetime import datetime
    
    # Obtenir l'utilisateur et son abonnement
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user or not user.subscription:
        return {"allowed": False, "reason": "Pas d'abonnement actif"}
    
    subscription = user.subscription
    limits = get_subscription_limits(subscription.tier)
    
    # Vérifier la date d'expiration
    if subscription.end_date and subscription.end_date < datetime.utcnow():
        return {"allowed": False, "reason": "Abonnement expiré"}
    
    # Vérifier les simulations mensuelles
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    
    usage = db_session.query(UsageStats).filter(
        UsageStats.user_id == user_id,
        UsageStats.month == current_month,
        UsageStats.year == current_year
    ).first()
    
    if usage:
        if limits["monthly_simulations"] != -1 and usage.simulations_count >= limits["monthly_simulations"]:
            return {"allowed": False, "reason": f"Limite mensuelle atteinte ({limits['monthly_simulations']} simulations)"}
        
        if limits["storage_mb"] != -1 and usage.storage_used_mb >= limits["storage_mb"]:
            return {"allowed": False, "reason": f"Limite de stockage atteinte ({limits['storage_mb']} MB)"}
    
    return {"allowed": True, "remaining_simulations": limits["monthly_simulations"] - (usage.simulations_count if usage else 0) if limits["monthly_simulations"] != -1 else -1}
