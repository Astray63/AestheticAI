# 🚀 Guide de Démarrage Rapide - AestheticAI

## ⚡ Démarrage en 2 minutes avec Docker

### 1. Prérequis
- [Docker](https://docs.docker.com/get-docker/) installé
- [Docker Compose](https://docs.docker.com/compose/install/) installé

### 2. Clone et démarrage
```bash
git clone https://github.com/votre-repo/aesthetic-ai.git
cd aesthetic-ai
npm run docker:dev
```

### 3. Accès à l'application
- 🎨 **Frontend** : http://localhost:3000
- ⚡ **API Backend** : http://localhost:8000
- 📚 **Documentation** : http://localhost:8000/docs

### 4. Connexion de test
- **Username** : `test_doctor`
- **PIN** : `123456`

---

## 📋 Commandes Essentielles

```bash
# 🚀 Démarrage
npm run docker:dev        # Mode développement
npm run docker:prod       # Mode production

# 🛠️ Gestion
npm run docker:stop       # Arrêter tous les services
npm run docker:logs       # Voir les logs
npm run docker:clean      # Nettoyer les containers

# 🧪 Tests
npm run test:docker       # Tests dans containers
npm run health            # Vérifier la santé des services

# 🧹 Maintenance
npm run cleanup           # Nettoyer caches et temporaires
```

---

## 🐳 Architecture Docker

### Mode Développement
- **Hot reload** activé pour frontend et backend
- **Volumes montés** pour développement en temps réel
- **Base de données** PostgreSQL temporaire
- **Ports exposés** : 3000 (frontend), 8000 (backend), 5432 (DB)

### Mode Production
- **Build optimisé** avec cache multi-stage
- **Nginx** comme reverse proxy
- **Base de données** persistante avec volumes
- **SSL/TLS** prêt pour le déploiement

---

## 🔧 Configuration Rapide

### Variables d'environnement
```bash
# Copier et modifier selon vos besoins
cp .env.dev .env           # Développement
cp .env.prod .env          # Production
```

### GPU pour l'IA (Optionnel)
```bash
# Dans votre fichier .env
USE_GPU=true
DEVICE=cuda
```

---

## 🆘 Dépannage Rapide

### Problèmes courants
```bash
# Ports déjà utilisés
npm run docker:stop && npm run docker:dev

# Problème de permissions
sudo chown -R $USER:$USER .

# Réinitialiser complètement
npm run docker:clean && npm run docker:dev

# Vérifier les logs
npm run docker:logs
```

### Support
- 📖 **Documentation complète** : [README.md](README.md)
- 🐳 **Guide Docker** : [DOCKER.md](DOCKER.md)
- 🐛 **Issues** : GitHub Issues
- 📧 **Contact** : support@aestheticai.com

---

**🎉 Votre application AestheticAI est prête !**
