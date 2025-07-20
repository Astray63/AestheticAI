"""
Script pour créer un utilisateur de test
"""
from sqlalchemy import create_engine, text
from database import DATABASE_URL
from auth import hash_pin
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_user():
    """Créer un utilisateur de test"""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    try:
        with engine.connect() as conn:
            # Vérifier si l'utilisateur test existe déjà
            result = conn.execute(text("SELECT id FROM users WHERE username = :username"), {"username": "test_doctor"})
            if result.fetchone():
                logger.info("L'utilisateur test existe déjà")
                return
            
            # Créer l'utilisateur
            hashed = hash_pin("123456")
            conn.execute(text("""
                INSERT INTO users (username, hashed_pin, full_name, speciality, license_number, is_active, created_at) 
                VALUES (:username, :hashed_pin, :full_name, :speciality, :license_number, 1, datetime('now'))
            """), {
                "username": "test_doctor",
                "hashed_pin": hashed,
                "full_name": "Dr. Test",
                "speciality": "Médecine Esthétique",
                "license_number": "TEST123456"
            })
            
            # Récupérer l'ID de l'utilisateur créé
            result = conn.execute(text("SELECT id FROM users WHERE username = :username"), {"username": "test_doctor"})
            user_id = result.fetchone()[0]
            
            # Créer son abonnement freemium
            conn.execute(text("""
                INSERT INTO subscriptions (user_id, tier, end_date) 
                VALUES (:user_id, 'freemium', datetime('now', '+1 year'))
            """), {"user_id": user_id})
            
            conn.commit()
            
        logger.info("Utilisateur de test créé avec succès!")
        logger.info("Login: test_doctor")
        logger.info("PIN: 123456")
            
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'utilisateur: {e}")
        raise

if __name__ == "__main__":
    create_test_user()
