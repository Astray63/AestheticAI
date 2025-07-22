from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta
import stripe
import os

from database import get_db, User
from subscription_models import (
    Subscription, Payment, UsageStats, 
    SubscriptionTier, PaymentStatus,
    get_subscription_limits, check_usage_limits
)
from auth import verify_token
from schemas import *

# Configuration Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_votre_cle_stripe")

# Sécurité
security = HTTPBearer()

def get_current_user_from_credentials(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Helper pour obtenir l'utilisateur actuel depuis le token"""
    payload = verify_token(credentials.credentials)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Token invalide")
    current_user = db.query(User).filter(User.username == username).first()
    if not current_user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    return current_user

router = APIRouter(prefix="/subscription", tags=["subscription"])

@router.get("/plans", response_model=Dict[str, Any])
async def get_subscription_plans():
    """Obtenir tous les plans d'abonnement disponibles"""
    plans = {}
    for tier in SubscriptionTier:
        limits = get_subscription_limits(tier)
        plans[tier.value] = {
            "name": tier.value.title(),
            "price": limits["price"],
            "features": {
                "monthly_simulations": limits["monthly_simulations"],
                "storage_mb": limits["storage_mb"],
                "advanced_ai": limits["advanced_ai"],
                "priority_support": limits["priority_support"],
                "white_label": limits["white_label"]
            },
            "description": get_plan_description(tier)
        }
    return {"plans": plans}

@router.get("/current", response_model=Dict[str, Any])
async def get_current_subscription(
    current_user: User = Depends(get_current_user_from_credentials),
    db: Session = Depends(get_db)
):
    """Obtenir l'abonnement actuel de l'utilisateur"""
    # Pour l'instant, retourner un abonnement freemium par défaut
    # sans utiliser la base de données (la table subscriptions n'existe pas encore)
    
    limits = get_subscription_limits(SubscriptionTier.FREEMIUM)
    
    return {
        "id": 1,
        "tier": "freemium",
        "status": "active",
        "start_date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
        "end_date": (datetime.utcnow() + timedelta(days=365)).isoformat(),
        "auto_renew": False,
        "limits": {
            "simulations_per_month": limits["monthly_simulations"],
            "storage_gb": limits["storage_mb"] / 1024,
            "api_calls_per_day": 1000,  # Valeur par défaut
            "max_patients": 50,  # Valeur par défaut
            "advanced_ai": limits["advanced_ai"],
            "priority_support": limits["priority_support"],
            "white_label": limits["white_label"]
        },
        "usage": {
            "simulations_used": 0,
            "storage_used_gb": 0,
            "api_calls_today": 0,
            "patients_count": 0
        }
    }
    
    # Obtenir les statistiques d'utilisation
    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year
    
    usage = db.query(UsageStats).filter(
        UsageStats.user_id == current_user.id,
        UsageStats.month == current_month,
        UsageStats.year == current_year
    ).first()
    
    if not usage:
        usage = UsageStats(
            user_id=current_user.id,
            month=current_month,
            year=current_year
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)
    
    limits = get_subscription_limits(subscription.tier)
    usage_check = check_usage_limits(current_user.id, db)
    
    return {
        "subscription": {
            "tier": subscription.tier.value,
            "start_date": subscription.start_date,
            "end_date": subscription.end_date,
            "is_active": subscription.is_active,
            "auto_renew": subscription.auto_renew
        },
        "limits": limits,
        "usage": {
            "simulations_count": usage.simulations_count,
            "storage_used_mb": usage.storage_used_mb,
            "ai_processing_time": usage.ai_processing_time_seconds
        },
        "usage_check": usage_check
    }

@router.post("/upgrade")
async def create_upgrade_session(
    plan_data: Dict[str, str],
    current_user: User = Depends(get_current_user_from_credentials),
    db: Session = Depends(get_db)
):
    """Créer une session de paiement Stripe pour upgrade"""
    try:
        tier_name = plan_data.get("tier")
        if not tier_name:
            raise HTTPException(status_code=400, detail="Tier requis")
        
        try:
            tier = SubscriptionTier(tier_name)
        except ValueError:
            raise HTTPException(status_code=400, detail="Tier invalide")
        
        limits = get_subscription_limits(tier)
        price = limits["price"]
        
        if price == 0:
            raise HTTPException(status_code=400, detail="Plan gratuit, pas de paiement requis")
        
        # Créer une session Stripe
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': f'AestheticAI {tier.value.title()}',
                        'description': get_plan_description(tier)
                    },
                    'unit_amount': int(price * 100),  # Convertir en centimes
                    'recurring': {
                        'interval': 'month'
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard?payment=success",
            cancel_url=f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/dashboard?payment=cancelled",
            client_reference_id=str(current_user.id),
            metadata={
                'user_id': current_user.id,
                'tier': tier_name
            }
        )
        
        return {"checkout_url": session.url, "session_id": session.id}
        
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=f"Erreur Stripe: {str(e)}")

@router.post("/webhook")
async def stripe_webhook(
    payload: bytes,
    stripe_signature: str,
    db: Session = Depends(get_db)
):
    """Webhook Stripe pour traiter les paiements"""
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    if not webhook_secret:
        raise HTTPException(status_code=400, detail="Webhook secret non configuré")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, webhook_secret
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Payload invalide")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Signature invalide")
    
    # Traiter l'événement
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        await handle_successful_payment(session, db)
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        await handle_recurring_payment(invoice, db)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        await handle_subscription_cancelled(subscription, db)
    
    return {"status": "success"}

@router.get("/usage", response_model=Dict[str, Any])
async def get_usage_statistics(
    current_user: User = Depends(get_current_user_from_credentials),
    db: Session = Depends(get_db)
):
    """Obtenir les statistiques d'utilisation détaillées"""
    # Obtenir les 12 derniers mois
    stats = []
    for i in range(12):
        date = datetime.utcnow() - timedelta(days=30 * i)
        usage = db.query(UsageStats).filter(
            UsageStats.user_id == current_user.id,
            UsageStats.month == date.month,
            UsageStats.year == date.year
        ).first()
        
        stats.append({
            "month": date.month,
            "year": date.year,
            "simulations": usage.simulations_count if usage else 0,
            "storage_mb": usage.storage_used_mb if usage else 0,
            "processing_time": usage.ai_processing_time_seconds if usage else 0
        })
    
    return {"usage_history": stats[::-1]}  # Inverser pour ordre chronologique

@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user_from_credentials),
    db: Session = Depends(get_db)
):
    """Annuler l'abonnement (reste actif jusqu'à la fin de la période)"""
    # Chercher l'abonnement directement
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Aucun abonnement actif")
    
    # Annuler l'auto-renouvellement
    subscription.auto_renew = False
    
    # Si il y a un abonnement Stripe, l'annuler
    if subscription.stripe_subscription_id:
        try:
            stripe.Subscription.delete(subscription.stripe_subscription_id)
        except stripe.error.StripeError as e:
            # Log l'erreur mais continue
            pass
    
    db.commit()
    
    return {"message": "Abonnement annulé. Reste actif jusqu'au " + subscription.end_date.strftime("%d/%m/%Y")}

# Fonctions utilitaires
def get_plan_description(tier: SubscriptionTier) -> str:
    descriptions = {
        SubscriptionTier.FREEMIUM: "Parfait pour découvrir AestheticAI avec 5 simulations par mois",
        SubscriptionTier.STARTER: "Idéal pour les petites cliniques avec IA avancée et 50 simulations/mois",
        SubscriptionTier.PROFESSIONAL: "Pour les professionnels avec support prioritaire et 200 simulations/mois",
        SubscriptionTier.ENTERPRISE: "Solution complète avec simulations illimitées et marque blanche"
    }
    return descriptions.get(tier, "")

async def handle_successful_payment(session, db: Session):
    """Traiter un paiement réussi"""
    user_id = int(session['metadata']['user_id'])
    tier_name = session['metadata']['tier']
    tier = SubscriptionTier(tier_name)
    
    # Mettre à jour l'abonnement
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.subscription:
        subscription = user.subscription
        subscription.tier = tier
        subscription.end_date = datetime.utcnow() + timedelta(days=30)
        subscription.is_active = True
        subscription.stripe_subscription_id = session.get('subscription')
        
        # Mettre à jour les limites
        limits = get_subscription_limits(tier)
        subscription.monthly_simulations_limit = limits["monthly_simulations"]
        subscription.storage_limit_mb = limits["storage_mb"]
        subscription.advanced_ai_features = limits["advanced_ai"]
        subscription.priority_support = limits["priority_support"]
        subscription.white_label = limits["white_label"]
        
        # Enregistrer le paiement
        payment = Payment(
            subscription_id=subscription.id,
            amount=limits["price"],
            status=PaymentStatus.PAID,
            stripe_payment_id=session['payment_intent']
        )
        db.add(payment)
        db.commit()

async def handle_recurring_payment(invoice, db: Session):
    """Traiter un paiement récurrent"""
    # Étendre la période d'abonnement
    pass

async def handle_subscription_cancelled(subscription_data, db: Session):
    """Traiter l'annulation d'un abonnement"""
    # Désactiver l'abonnement dans la base
    pass
