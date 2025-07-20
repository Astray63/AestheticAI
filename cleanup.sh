#!/bin/bash

# Script de nettoyage automatique pour AestheticAI
# Usage: ./cleanup.sh

echo "🧹 Nettoyage automatique d'AestheticAI..."

# Suppression des caches Python
echo "🐍 Suppression des caches Python..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "*.pyo" -delete 2>/dev/null || true

# Suppression des caches Node.js temporaires
echo "📦 Nettoyage des caches Node.js..."
rm -rf frontend/.eslintcache 2>/dev/null || true
rm -rf frontend/node_modules/.cache 2>/dev/null || true

# Suppression des rapports de couverture temporaires
echo "📊 Suppression des rapports de couverture temporaires..."
rm -rf backend/htmlcov 2>/dev/null || true
rm -rf backend/.coverage 2>/dev/null || true
rm -rf backend/.pytest_cache 2>/dev/null || true
rm -rf backend/.mypy_cache 2>/dev/null || true

# Suppression des logs temporaires
echo "📝 Suppression des logs temporaires..."
find . -name "*.log" -delete 2>/dev/null || true

# Suppression des fichiers de sauvegarde
echo "💾 Suppression des fichiers de sauvegarde..."
find . -name "*~" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
find . -name ".DS_Store" -delete 2>/dev/null || true
find . -name "Thumbs.db" -delete 2>/dev/null || true

# Suppression des fichiers d'environnement de test
echo "🔧 Nettoyage des fichiers temporaires de développement..."
rm -rf .vscode/.ropeproject 2>/dev/null || true

# Vérification de la taille libérée
echo "✅ Nettoyage terminé!"
echo "📊 Statistiques du projet après nettoyage:"
du -sh . 2>/dev/null || echo "Impossible de calculer la taille du projet"

echo ""
echo "🎯 Suggestions post-nettoyage:"
echo "  - Exécuter 'npm run lint' dans frontend/"
echo "  - Exécuter 'flake8 .' dans backend/"
echo "  - Vérifier que tous les tests passent"
