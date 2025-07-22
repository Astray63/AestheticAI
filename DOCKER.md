# 🐳 AestheticAI - Configuration Docker

Configuration Docker complète pour déployer facilement l'application AestheticAI de médecine esthétique.

## 🚀 Démarrage ultra-rapide

```bash
# Cloner et démarrer en 2 commandes
git clone <votre-repo>
cd App-Medical
./start.sh dev
```

**C'est tout !** L'application sera disponible sur http://localhost:3000

## 📋 Commandes essentielles

```bash
# DÉVELOPPEMENT
./start.sh dev              # Démarrer en mode dev (hot reload)
./start.sh logs             # Voir les logs en temps réel

# PRODUCTION  
./start.sh prod             # Démarrer en mode production
./start.sh stop             # Arrêter tous les services
./start.sh restart          # Redémarrer

# MAINTENANCE
./start.sh status           # Voir l'état des services
./start.sh clean            # Nettoyer tout (attention !)
```

## 🌐 Accès aux services

### Mode Développement
- **🎨 Frontend** : http://localhost:3000 (React avec hot reload)
- **⚡ Backend API** : http://localhost:8000 (FastAPI)
- **📚 Documentation** : http://localhost:8000/docs (Swagger)
- **🗄️ Base de données** : localhost:5432 (PostgreSQL)

### Mode Production  
- **🌍 Application** : http://localhost:80 (tout-en-un)
- **📡 API** : http://localhost:80/api
- **📖 Docs** : http://localhost:80/docs

## 🏗️ Architecture Docker

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │────│    Frontend     │────│    Backend      │
│ (Reverse Proxy) │    │   (React SPA)   │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      Redis      │    │   Volumes       │
│  (Base données) │    │    (Cache)      │    │ (Persistence)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration rapide

### Variables importantes (.env)
```bash
# Base de données
DATABASE_URL=postgresql://user:password@postgres:5432/aesthetic_db

# Sécurité  
SECRET_KEY=changez-moi-en-production

# IA
USE_GPU=false  # true si vous avez une GPU NVIDIA
MODEL_NAME=stabilityai/stable-diffusion-2-1
```

## 🔒 Utilisateur de test

**PIN** : `1234`  
**Email** : `test@aesthetic-ai.com`

## 🚨 Troubleshooting

### Problème de port occupé
```bash
./start.sh stop
sudo lsof -ti:3000 | xargs kill -9  # Frontend
sudo lsof -ti:8000 | xargs kill -9  # Backend
```

### Rebuild complet
```bash
./start.sh clean
./start.sh build --no-cache
./start.sh dev
```

### Logs détaillés
```bash
./start.sh logs backend     # Logs backend uniquement
./start.sh logs frontend    # Logs frontend uniquement
./start.sh logs postgres    # Logs base de données
```

## 📂 Structure des fichiers Docker

```
├── docker-compose.yml          # 🏭 Production
├── docker-compose.dev.yml      # 🛠️ Développement  
├── start.sh                    # 🚀 Script de démarrage
├── .env                        # ⚙️ Config production
├── .env.dev                    # ⚙️ Config développement
├── backend/
│   ├── Dockerfile              # 🐳 Image backend prod
│   └── Dockerfile.dev          # 🐳 Image backend dev
├── frontend/  
│   ├── Dockerfile              # 🐳 Image frontend prod
│   └── Dockerfile.dev          # 🐳 Image frontend dev
└── docker/
    └── nginx/                  # 🔀 Configuration proxy
```

## 🎯 Commandes Docker avancées

```bash
# Accéder aux containers
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec postgres psql -U aesthetic_user -d aesthetic_db

# Monitoring
docker stats                    # Usage CPU/RAM en temps réel
docker-compose logs -f backend  # Logs backend en continu

# Maintenance  
docker system prune -a          # Nettoyer tout Docker
docker volume ls                # Lister les volumes
```

## 🔄 Workflow de développement

1. **Démarrer** : `./start.sh dev`
2. **Coder** : Les changements sont automatiquement pris en compte
3. **Tester** : http://localhost:3000 + http://localhost:8000/docs
4. **Déboguer** : `./start.sh logs`
5. **Arrêter** : `./start.sh stop`

## 🚀 Déploiement production

```bash
# 1. Configurer les variables
cp .env.example .env
nano .env  # Modifier SECRET_KEY, DATABASE_URL, etc.

# 2. Déployer
./start.sh prod

# 3. Vérifier
./start.sh status
curl http://localhost/health
```

## 💡 Tips & Astuces

- **Performance** : Activez `USE_GPU=true` si vous avez une GPU NVIDIA
- **Développement** : Utilisez toujours le mode `dev` pour le hot reload
- **Production** : Le mode `prod` optimise les assets et active la compression
- **Sécurité** : Changez TOUJOURS `SECRET_KEY` en production
- **Monitoring** : Nginx logs sont dans `/var/log/nginx/` du container

---

💬 **Besoin d'aide ?** Consultez `docker/README.md` pour plus de détails ou ouvrez une issue.
