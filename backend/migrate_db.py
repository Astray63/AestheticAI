"""
Script de migration pour ajouter les tables d'abonnement
"""
from sqlalchemy import create_engine, text
from database import DATABASE_URL
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migrer la base de données pour ajouter les nouvelles tables"""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    
    try:
        logger.info("Création des nouvelles tables d'abonnement...")
        
        # Créer les tables manuellement avec SQL
        with engine.connect() as conn:
            # Table subscriptions
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER UNIQUE,
                    tier TEXT DEFAULT 'freemium',
                    start_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    end_date DATETIME,
                    is_active BOOLEAN DEFAULT 1,
                    auto_renew BOOLEAN DEFAULT 1,
                    monthly_simulations_limit INTEGER DEFAULT 5,
                    storage_limit_mb INTEGER DEFAULT 100,
                    advanced_ai_features BOOLEAN DEFAULT 0,
                    priority_support BOOLEAN DEFAULT 0,
                    white_label BOOLEAN DEFAULT 0,
                    stripe_subscription_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """))
            
            # Table payments
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY,
                    subscription_id INTEGER,
                    amount REAL,
                    currency TEXT DEFAULT 'EUR',
                    status TEXT DEFAULT 'pending',
                    payment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                    stripe_payment_id TEXT,
                    invoice_url TEXT,
                    FOREIGN KEY(subscription_id) REFERENCES subscriptions(id)
                )
            """))
            
            # Table usage_stats
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    month INTEGER,
                    year INTEGER,
                    simulations_count INTEGER DEFAULT 0,
                    storage_used_mb REAL DEFAULT 0.0,
                    ai_processing_time_seconds REAL DEFAULT 0.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """))
            
            conn.commit()
            
            # Créer des abonnements freemium pour tous les utilisateurs existants
            result = conn.execute(text("SELECT id FROM users"))
            users = result.fetchall()
            
            for user in users:
                user_id = user[0]
                # Vérifier si l'utilisateur a déjà un abonnement
                result = conn.execute(text("SELECT id FROM subscriptions WHERE user_id = :user_id"), {"user_id": user_id})
                if not result.fetchone():
                    conn.execute(text("""
                        INSERT INTO subscriptions (user_id, tier, end_date) 
                        VALUES (:user_id, 'freemium', datetime('now', '+1 year'))
                    """), {"user_id": user_id})
                    logger.info(f"Abonnement freemium créé pour l'utilisateur {user_id}")
            
            conn.commit()
            
        logger.info("Migration terminée avec succès!")
            
    except Exception as e:
        logger.error(f"Erreur lors de la migration: {e}")
        raise

if __name__ == "__main__":
    migrate_database()
