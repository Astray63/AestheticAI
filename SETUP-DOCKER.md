# 🐳 SETUP DOCKER - AestheticAI

Ce guide vous aide à démarrer l'application AestheticAI avec Docker en quelques minutes.

## ⚡ Démarrage ultra-rapide

1. **Cloner le projet**
```bash
git clone <votre-repo>
cd App-Medical
```

2. **Démarrer l'application**
```bash
./quick-start.sh
```

3. **Accéder à l'application**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Docs: http://localhost:8000/docs

## 🛠️ Commandes utiles

```bash
# Démarrer
./quick-start.sh

# Voir les logs
docker compose -f docker-compose.dev.yml logs -f

# Arrêter  
docker compose -f docker-compose.dev.yml down

# Redémarrer après modifications
docker compose -f docker-compose.dev.yml restart

# Accéder à un container
docker compose -f docker-compose.dev.yml exec backend bash
docker compose -f docker-compose.dev.yml exec frontend sh
```

## 🔐 Compte de test

- **PIN**: `1234`
- **Email**: `test@aesthetic-ai.com`

## 🐛 Problèmes courants

### Port déjà utilisé
```bash
# Voir les processus sur les ports
sudo lsof -i :3000
sudo lsof -i :8000

# Tuer les processus
sudo lsof -ti:3000 | xargs kill -9
sudo lsof -ti:8000 | xargs kill -9
```

### Rebuild complet
```bash
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml build --no-cache
docker compose -f docker-compose.dev.yml up -d
```

## 📦 Ce qui est inclus

- **Frontend React** avec hot reload
- **Backend FastAPI** avec auto-reload  
- **PostgreSQL** pour la base de données
- **Volumes** pour la persistence des données
- **Variables d'environnement** pré-configurées

## 🚀 Mode production

Pour tester en mode production :
```bash
./start.sh prod
```

Accès: http://localhost:80

---

**Note**: Si vous rencontrez des problèmes, consultez `DOCKER.md` pour plus de détails.
