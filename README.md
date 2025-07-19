# AestheticAI - Application de Médecine Esthétique avec IA

## 🎯 Vue d'ensemble

AestheticAI est une application complète pour les professionnels de la médecine esthétique, permettant de simuler les résultats d'interventions en utilisant l'intelligence artificielle générative.

## ✨ Fonctionnalités

- **📸 Capture d'images** : Prise de photo directe ou upload de fichier
- **🎨 Simulation IA** : Génération de résultats réalistes avec Stable Diffusion + ControlNet  
- **⚡ Génération rapide** : Résultats en moins de 2 minutes
- **🔒 Sécurité maximale** : Authentification PIN, chiffrement des données patients
- **📱 Interface responsive** : Optimisée mobile et desktop
- **👨‍⚕️ Interface professionnelle** : Conçue pour les professionnels de santé

## 🏗️ Architecture

### Backend (Python - FastAPI)
- **API RESTful** avec FastAPI
- **Base de données** SQLite (développement) / PostgreSQL (production)
- **IA générative** avec Stable Diffusion + ControlNet
- **Authentification** JWT avec PIN
- **Upload sécurisé** d'images

### Frontend (React + TypeScript)
- **Interface moderne** avec React 18 + TypeScript
- **Design system** avec Tailwind CSS
- **Gestion d'état** avec Context API
- **Capture webcam** intégrée
- **Responsive design** mobile-first

### Interventions supportées
- **Lèvres** : Injection d'acide hyaluronique (0.5-5ml)
- **Pommettes** : Volumisation (1-8ml)  
- **Menton** : Redéfinition (1-6ml)
- **Front** : Botox (10-50 unités)

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.9+ 
- Node.js 16+
- npm ou yarn

### 1. Backend Setup

```bash
cd backend

# Installer les dépendances
pip install -r requirements.txt

# Copier la configuration
cp .env.example .env

# Démarrer le serveur
python run.py
```

Le backend sera accessible sur `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Installer les dépendances  
npm install

# Démarrer le serveur de développement
npm start
```

Le frontend sera accessible sur `http://localhost:3000`

## 🔧 Configuration

### Backend
Modifier le fichier `.env` pour configurer :
- `USE_GPU=true` : Activer le GPU pour l'IA (recommandé)
- `SECRET_KEY` : Clé de chiffrement (à changer en production)
- `DATABASE_URL` : URL de la base de données

### Frontend
Créer un fichier `.env.local` :
```
REACT_APP_API_URL=http://localhost:8000
```

## 👤 Utilisation

### Première connexion
1. Créer un compte professionnel (nom d'utilisateur + PIN 6 chiffres)
2. Renseigner spécialité et numéro de licence

### Workflow typique
1. **Créer un patient** avec âge, genre, type de peau (données anonymisées)
2. **Sélectionner l'intervention** et la dose
3. **Prendre/uploader une photo** du patient
4. **Lancer la simulation** (2 min max)
5. **Visualiser le résultat** avant/après
6. **Télécharger** ou présenter au patient

## 🤖 IA et Modèles

### Modèles utilisés
- **Stable Diffusion v1.5** : Génération d'images de base
- **ControlNet Canny** : Contrôle de la structure faciale
- **Preprocessing** : Détection des contours avec OpenCV

### Mode Mock (Développement)
En l'absence de GPU, l'application fonctionne en mode "mock" :
- Simule le temps de traitement (2s)
- Retourne une version légèrement modifiée de l'image originale
- Permet de tester l'interface sans matériel spécialisé

### Production avec GPU
Pour une utilisation réelle :
1. Installer CUDA + PyTorch GPU
2. Configurer `USE_GPU=true`
3. Les modèles seront téléchargés automatiquement (~5GB)

## 🔐 Sécurité et RGPD

### Données patients
- **Anonymisation** automatique avec UUID
- **Chiffrement** des images uploadées
- **Suppression** automatique après 30 jours
- **Logs auditables** des accès

### Authentification
- **PIN à 6 chiffres** (bcrypt hashé)
- **Tokens JWT** avec expiration
- **Sessions sécurisées** HTTPS uniquement en production

## 📊 API Documentation

Une fois le backend démarré, la documentation interactive est disponible sur :
- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

### Endpoints principaux
- `POST /auth/login` : Connexion
- `POST /patients` : Créer un patient
- `POST /simulations` : Lancer une simulation  
- `GET /simulations/{id}` : Récupérer une simulation
- `GET /images/{filename}` : Accéder aux images

## 🧪 Tests et Qualité

### Backend
```bash
cd backend
pytest tests/ -v
```

### Frontend  
```bash
cd frontend
npm test
```

### Linting
```bash
# Backend
flake8 .
black .

# Frontend
npm run lint
npm run format
```

## 🚀 Déploiement

### Docker (Recommandé)
```bash
# Build et démarrage
docker-compose up -d

# Logs
docker-compose logs -f
```

### Production
1. **Backend** : Déployer sur serveur avec GPU (AWS EC2 p3, Google Cloud GPU)
2. **Frontend** : Build static + CDN (Netlify, Vercel)
3. **Base de données** : PostgreSQL managée (AWS RDS, Google Cloud SQL)
4. **Stockage** : S3 ou Google Cloud Storage pour les images

## 📈 Monitoring

### Métriques importantes
- **Temps de génération IA** (objectif < 2min)
- **Taux de succès** des simulations  
- **Usage GPU** et mémoire
- **Temps de réponse API**

### Outils recommandés
- **Prometheus** + **Grafana** : Métriques
- **Sentry** : Monitoring des erreurs
- **ELK Stack** : Logs centralisés

## 🤝 Contribution

### Standards de code
- **Python** : PEP 8, type hints, docstrings
- **TypeScript** : ESLint, Prettier, interfaces strictes
- **Git** : Conventional commits
- **Documentation** : Markdown, JSDoc

### Workflow
1. Fork le repository
2. Créer une branche feature
3. Tests + linting
4. Pull request avec description détaillée

## 📄 Licence

**Usage professionnel uniquement**. Conforme aux réglementations médicales européennes et RGPD.

## 🆘 Support

- **Documentation** : `/docs`
- **Issues** : GitHub Issues
- **Email** : support@aestheticai.com

---

*Développé avec ❤️ pour les professionnels de la médecine esthétique*
