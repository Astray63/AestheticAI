# 🌟 AestheticAI - SaaS de Médecine Esthétique avec IA

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/votre-repo/aesthetic-ai)
[![License](https://img.shields.io/badge/license-PROPRIETARY-red.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-19.1.0-blue.svg)](https://reactjs.org)

## 🚀 Présentation

AestheticAI est la première plateforme SaaS dédiée aux professionnels de la médecine esthétique, utilisant l'intelligence artificielle avancée pour générer des simulations d'interventions ultra-réalistes.

### ✨ Fonctionnalités Principales

- 🧠 **IA Avancée** : Technologie Stable Diffusion pour des simulations photo-réalistes
- 🔒 **RGPD Compliant** : Protection totale des données patients
- ⚡ **Temps Réel** : Génération de simulations en moins de 30 secondes
- 👥 **Multi-praticiens** : Gestion de cabinet avec accès sécurisé
- 📊 **Système d'abonnement** : 4 niveaux (Freemium, Starter, Professional, Enterprise)
- 🎯 **Interventions Supportées** : Lèvres, nez, joues, menton, rides, etc.
- 📱 **Responsive** : Interface optimisée desktop et mobile

## 🏗️ Architecture Technique

### Backend (FastAPI + Python)
- **Framework** : FastAPI avec Uvicorn
- **Base de données** : SQLite avec SQLAlchemy ORM
- **IA** : Stable Diffusion + ControlNet pour les simulations
- **Authentification** : JWT avec codes PIN sécurisés
- **Paiements** : Intégration Stripe pour les abonnements
- **Sécurité** : Hashage bcrypt, validation Pydantic

### Frontend (React + TypeScript)
- **Framework** : React 19 avec TypeScript
- **Styling** : Tailwind CSS pour un design moderne
- **Navigation** : React Router pour le routing
- **État** : Context API pour l'authentification
- **Icons** : Lucide React pour les icônes
- **Build** : Create React App avec optimisations

## � Installation

> 🚀 **Démarrage rapide** : Consultez [QUICKSTART.md](QUICKSTART.md) pour un démarrage en 2 minutes avec Docker !

### Prérequis
- Python 3.11+
- Node.js 16+
- Docker & Docker Compose (recommandé)

### 🐳 Démarrage avec Docker (Recommandé)
```bash
git clone https://github.com/votre-repo/aesthetic-ai.git
cd aesthetic-ai
npm run docker:dev
```

Accès immédiat :
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Documentation API : http://localhost:8000/docs

### 🛠️ Démarrage manuel (développement)

### 1. Cloner le repository
```bash
git clone https://github.com/votre-repo/aesthetic-ai.git
cd aesthetic-ai
```

### 2. Configuration de l'environnement
```bash
# Créer l'environnement virtuel Python
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate  # Windows

# Installer les dépendances
npm run install:all
```

### 3. Configuration des variables d'environnement
```bash
cp backend/.env.example backend/.env
# Éditer le fichier .env avec vos configurations
```

### 4. Migration de la base de données
```bash
cd backend
python migrate_db.py
python create_test_user.py  # Créer un utilisateur de test
```

### 5. Démarrage de l'application
```bash
npm run dev
```

L'application sera accessible sur :
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Documentation API : http://localhost:8000/docs

## 🔐 Authentification de Test

**Utilisateur de test créé automatiquement :**
- **Login** : `test_doctor`
- **PIN** : `123456`

## 💎 Plans d'Abonnement

### 🆓 Freemium
- **Prix** : Gratuit
- **Simulations** : 5/mois
- **Fonctionnalités** : Base IA, Support email

### 🌱 Starter
- **Prix** : 29€/mois
- **Simulations** : 50/mois
- **Fonctionnalités** : IA avancée, Support prioritaire, Historique

### 🚀 Professional
- **Prix** : 99€/mois
- **Simulations** : 200/mois
- **Fonctionnalités** : Multi-praticiens, API access, Analytics

### 🏢 Enterprise
- **Prix** : 299€/mois
- **Simulations** : Illimité
- **Fonctionnalités** : Tout inclus, Support dédié, Personnalisation

## 🛠️ Développement

### Structure du Projet
```
App-Medical/
├── backend/                 # 🐍 API FastAPI
│   ├── app/                # 🏗️ Architecture modulaire
│   │   ├── core/          # ⚙️ Configuration & DB
│   │   ├── models/        # 📊 Modèles SQLAlchemy
│   │   ├── schemas/       # 📋 Schémas Pydantic
│   │   ├── services/      # 🔧 Logique métier
│   │   ├── api/           # 🚀 Endpoints FastAPI
│   │   └── utils/         # 🛠️ Utilitaires
│   ├── tests/             # 🧪 Tests backend
│   ├── Dockerfile         # 🐳 Image production
│   └── requirements.txt   # 📦 Dépendances Python
├── frontend/               # ⚛️ Application React
│   ├── src/
│   │   ├── components/    # 🧩 Composants React
│   │   ├── services/      # 🌐 API clients
│   │   ├── hooks/         # 🪝 Hooks personnalisés
│   │   └── types.ts       # 📝 Types TypeScript
│   ├── cypress/           # 🧪 Tests E2E
│   └── Dockerfile         # 🐳 Image production
├── docker/                # 🐳 Configuration Docker
│   └── nginx/             # 🔀 Reverse proxy
├── docker-compose.yml     # 🏭 Orchestration production
├── docker-compose.dev.yml # 🛠️ Orchestration développement
└── start.sh              # 🚀 Script de démarrage
```

### Scripts NPM Disponibles

```bash
# 🚀 Démarrage rapide avec Docker
npm run docker:dev          # Démarre tout avec Docker (dev)
npm run docker:prod         # Démarre tout avec Docker (prod)
npm run docker:stop         # Arrête tous les containers

# 🛠️ Développement local (sans Docker)
npm run dev                 # Frontend + Backend local
npm run dev:frontend        # Frontend seul (port 3000)
npm run dev:backend         # Backend seul (port 8000)

# 📦 Installation et Build
npm run install:all         # Installe toutes les dépendances
npm run build               # Build production frontend
npm run build:docker        # Build images Docker

# 🧪 Tests
npm run test                # Tests frontend (Jest)
npm run test:backend        # Tests backend (pytest)
npm run test:e2e            # Tests E2E (Cypress)
npm run test:docker         # Tests dans containers
npm run test:coverage       # Coverage complète

# 🔧 Maintenance
npm run cleanup             # Nettoie les caches et temporaires
npm run logs                # Affiche les logs Docker
npm run health              # Vérifie la santé des services
```

### Configuration Stripe

1. Créer un compte Stripe et récupérer les clés API
2. Configurer les webhooks Stripe :
   ```
   Endpoint URL: https://votre-domaine.com/api/webhooks/stripe
   Événements: customer.subscription.created, customer.subscription.updated, customer.subscription.deleted
   ```
3. Ajouter les clés dans `.env` :
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```

### Variables d'Environnement

Créer un fichier `backend/.env` :

```env
# Base de données
DATABASE_URL=sqlite:///./aesthetic_app.db

# JWT
SECRET_KEY=votre_clé_secrète_très_longue_et_complexe
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Stripe
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# IA (Hugging Face)
HUGGINGFACE_TOKEN=hf_your_token_here

# Environnement
ENVIRONMENT=development
DEBUG=true
```

## 🧪 Tests

### Tests Backend (pytest)
```bash
cd backend
pytest tests/ -v --cov=. --cov-report=html
```

### Tests Frontend (Jest)
```bash
cd frontend
npm test -- --coverage
```

### Tests E2E (Cypress)
```bash
cd frontend
npm run test:e2e
```

## 🚀 Déploiement

### Production avec Docker

```bash
# Build des images
docker-compose build

# Démarrage en production
docker-compose up -d

# Vérifier les logs
docker-compose logs -f
```

### Déploiement Manuel

1. **Backend** (ex: Railway, Heroku)
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

2. **Frontend** (ex: Vercel, Netlify)
   ```bash
   cd frontend
   npm run build
   # Déployer le dossier build/
   ```

## 📊 Monitoring

- **Logs** : Disponibles via `docker-compose logs`
- **Métriques** : Endpoint `/metrics` (Prometheus)
- **Santé** : Endpoint `/health` pour le health check
- **Coverage** : Rapports dans `htmlcov/` (backend) et `coverage/` (frontend)

## 🔒 Sécurité

- ✅ **Authentification JWT** avec rotation des tokens
- ✅ **Validation Pydantic** sur tous les endpoints
- ✅ **Hashage bcrypt** pour les PINs
- ✅ **CORS configuré** pour la production
- ✅ **Rate limiting** pour prévenir les abus
- ✅ **Validation des uploads** d'images
- ✅ **RGPD compliant** avec gestion des données

## 📈 Performance

- ⚡ **Génération IA** : < 30 secondes
- 🚀 **API Response** : < 200ms
- 📱 **Lighthouse Score** : 95+ sur mobile
- 🎯 **Uptime** : 99.9% SLA

## 🛟 Support

- 📧 **Email** : support@aesthetic-ai.com
- 📖 **Documentation** : API docs sur `/docs`
- 🐛 **Bugs** : GitHub Issues
- 💬 **Chat** : Support intégré pour Enterprise

## 📄 Licence

© 2024 AestheticAI. Tous droits réservés. 
**Usage professionnel uniquement**. Conforme aux réglementations médicales européennes et RGPD.

## 🆘 Support

- 📖 **Documentation** : `/docs` et [Docker Setup](DOCKER.md)
- � **Issues** : GitHub Issues
- 📧 **Email** : support@aestheticai.com

---

*Développé avec ❤️ pour les professionnels de la médecine esthétique*
