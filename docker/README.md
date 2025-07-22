# 🐳 Configuration Docker pour AestheticAI

Ce répertoire contient toute la configuration Docker nécessaire pour faire tourner l'application AestheticAI facilement.

## 🚀 Démarrage rapide

### Prérequis
- Docker (version 20.10+)
- Docker Compose (version 2.0+)

### Installation
```bash
# Cloner le projet
git clone <votre-repo>
cd App-Medical

# Démarrer en mode développement
./start.sh dev

# Ou démarrer en mode production
./start.sh prod
```

## 📋 Commandes disponibles

Le script `start.sh` simplifie la gestion de l'application :

```bash
# Développement
./start.sh dev              # Démarrer en mode développement
./start.sh dev --no-cache   # Reconstruire sans cache

# Production
./start.sh prod             # Démarrer en mode production
./start.sh prod --no-cache  # Reconstruire sans cache

# Gestion
./start.sh stop             # Arrêter tous les services
./start.sh restart          # Redémarrer
./start.sh status           # Voir le statut
./start.sh logs             # Voir tous les logs
./start.sh logs backend     # Voir les logs d'un service spécifique

# Maintenance
./start.sh build            # Construire les images
./start.sh clean            # Nettoyer containers et volumes
```

## 🏗️ Architecture

### Mode Développement (`docker-compose.dev.yml`)
- **Frontend** : React avec hot reload sur le port 3000
- **Backend** : FastAPI avec auto-reload sur le port 8000
- **Database** : PostgreSQL sur le port 5432
- Volumes montés pour le développement en temps réel

### Mode Production (`docker-compose.yml`)
- **Frontend** : Build optimisé servi par Nginx
- **Backend** : FastAPI avec plusieurs workers
- **Database** : PostgreSQL avec persistence
- **Reverse Proxy** : Nginx pour le routage
- **Cache** : Redis pour les performances
- Optimisé pour la performance et la sécurité

## 🌐 Accès aux services

### Mode Développement
- **Application Frontend** : http://localhost:3000
- **API Backend** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **Base de données** : localhost:5432

### Mode Production
- **Application complète** : http://localhost:80
- **API** : http://localhost:80/api
- **Documentation API** : http://localhost:80/docs

## 🔧 Configuration

### Variables d'environnement
- `.env` : Configuration production
- `.env.dev` : Configuration développement

### Principales variables :
```bash
# Base de données
DATABASE_URL=postgresql://user:password@postgres:5432/db
SECRET_KEY=your-secret-key

# IA
USE_GPU=false
MODEL_NAME=stabilityai/stable-diffusion-2-1
```

## 📁 Structure Docker

```
docker/
├── nginx/
│   ├── nginx.conf          # Configuration Nginx principale
│   └── frontend.conf       # Configuration spécifique frontend
backend/
├── Dockerfile              # Image production backend
└── Dockerfile.dev          # Image développement backend
frontend/
├── Dockerfile              # Image production frontend
└── Dockerfile.dev          # Image développement frontend
```

## 🔒 Sécurité

### Configuration Nginx
- Headers de sécurité (HSTS, CSP, etc.)
- Limitation de taille des uploads (50MB)
- Compression gzip activée
- Cache optimisé pour les assets statiques

### Backend
- Utilisateur non-root dans les containers
- Variables d'environnement sécurisées
- Health checks configurés

## 📊 Monitoring

### Health Checks
Tous les services ont des health checks configurés :
- **Frontend** : `curl -f http://localhost/`
- **Backend** : `curl -f http://localhost:8000/health`
- **Database** : `pg_isready`

### Logs
```bash
# Voir tous les logs
./start.sh logs

# Logs d'un service spécifique
./start.sh logs backend
./start.sh logs frontend
./start.sh logs postgres
```

## 🚀 Déploiement

### Développement local
```bash
./start.sh dev
```

### Test de production en local
```bash
./start.sh prod
```

### Production (serveur)
1. Configurer les variables d'environnement production
2. Modifier les domaines dans `.env`
3. Configurer SSL si nécessaire
4. Démarrer avec `./start.sh prod`

## 🛠️ Troubleshooting

### Problèmes courants

**Ports déjà utilisés :**
```bash
# Vérifier les ports
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8000

# Arrêter les services
./start.sh stop
```

**Problème de permissions :**
```bash
# Corriger les permissions
sudo chown -R $USER:$USER ./backend/uploads
sudo chown -R $USER:$USER ./backend/models
```

**Reconstruire complètement :**
```bash
./start.sh clean
./start.sh build --no-cache
./start.sh prod
```

## 📝 Logs et Debug

### Accéder aux containers
```bash
# Backend
docker-compose exec backend bash

# Frontend
docker-compose exec frontend sh

# Database
docker-compose exec postgres psql -U aesthetic_user -d aesthetic_db
```

### Vérifier la configuration
```bash
# Voir les variables d'environnement
docker-compose exec backend env

# Tester la connectivité base de données
docker-compose exec backend python -c "from database import engine; print('DB OK')"
```

## 🔄 Mise à jour

```bash
# Arrêter les services
./start.sh stop

# Mettre à jour le code
git pull

# Reconstruire et redémarrer
./start.sh build --no-cache
./start.sh prod
```
