#!/bin/bash

# 🧹 Script de nettoyage automatique pour AestheticAI
# Usage: ./cleanup.sh [--docker] [--deep] [--dry-run]

set -e

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Variables
DRY_RUN=false
DOCKER_CLEAN=false
DEEP_CLEAN=false

# Traiter les arguments
for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --docker)
            DOCKER_CLEAN=true
            shift
            ;;
        --deep)
            DEEP_CLEAN=true
            shift
            ;;
        *)
            ;;
    esac
done

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Fonction pour exécuter ou simuler
run_command() {
    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY-RUN]${NC} $1"
    else
        eval "$1"
    fi
}

echo -e "${BLUE}🧹 Nettoyage automatique d'AestheticAI...${NC}"
echo ""

# Suppression des caches Python
print_info "🐍 Suppression des caches Python..."
run_command "find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true"
run_command "find . -name '*.pyc' -delete 2>/dev/null || true"
run_command "find . -name '*.pyo' -delete 2>/dev/null || true"

# Suppression des caches Node.js temporaires
print_info "📦 Nettoyage des caches Node.js..."
run_command "rm -rf frontend/.eslintcache 2>/dev/null || true"
run_command "rm -rf frontend/node_modules/.cache 2>/dev/null || true"

# Suppression des rapports de couverture temporaires
print_info "📊 Suppression des rapports de couverture temporaires..."
run_command "rm -rf backend/htmlcov 2>/dev/null || true"
run_command "rm -rf backend/.coverage 2>/dev/null || true"
run_command "rm -rf backend/.pytest_cache 2>/dev/null || true"
run_command "rm -rf backend/.mypy_cache 2>/dev/null || true"
run_command "rm -rf frontend/coverage 2>/dev/null || true"

# Suppression des logs temporaires
print_info "📝 Suppression des logs temporaires..."
run_command "find . -name '*.log' -delete 2>/dev/null || true"
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
