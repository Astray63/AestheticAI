#!/bin/bash

# Script de test complet pour AestheticAI
# Usage: ./run-all-tests.sh [frontend|backend|e2e|all]

set -e  # Arrêter sur erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction d'affichage
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier les prérequis
check_prerequisites() {
    print_status "Vérification des prérequis..."
    
    # Vérifier Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js n'est pas installé"
        exit 1
    fi
    
    # Vérifier Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    # Vérifier npm
    if ! command -v npm &> /dev/null; then
        print_error "npm n'est pas installé"
        exit 1
    fi
    
    print_success "Tous les prérequis sont installés"
}

# Tests Frontend
run_frontend_tests() {
    print_status "Démarrage des tests frontend..."
    
    cd frontend
    
    # Installation des dépendances si nécessaire
    if [ ! -d "node_modules" ]; then
        print_status "Installation des dépendances frontend..."
        npm install
    fi
    
    # Linting
    print_status "Linting du code frontend..."
    npm run lint || {
        print_error "Échec du linting frontend"
        return 1
    }
    
    # Type checking
    print_status "Vérification des types TypeScript..."
    npm run type-check || {
        print_warning "Erreurs de types détectées"
    }
    
    # Tests unitaires
    print_status "Exécution des tests unitaires frontend..."
    CI=true npm test -- --coverage --watchAll=false || {
        print_error "Échec des tests unitaires frontend"
        return 1
    }
    
    # Build
    print_status "Build de l'application frontend..."
    npm run build || {
        print_error "Échec du build frontend"
        return 1
    }
    
    cd ..
    print_success "Tests frontend terminés avec succès"
}

# Tests Backend
run_backend_tests() {
    print_status "Démarrage des tests backend..."
    
    cd backend
    
    # Vérifier l'environnement virtuel
    if [ ! -f "../venv/bin/activate" ]; then
        print_status "Création ou recréation de l'environnement virtuel..."
        rm -rf ../venv
        python3 -m venv ../venv
    fi
    
    # Activer l'environnement virtuel
    source ../venv/bin/activate
    
    # Installation des dépendances
    print_status "Installation des dépendances backend..."
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-cov httpx pytest-mock
    
    # Linting
    print_status "Linting du code backend..."
    pip install flake8 black
    flake8 . --max-line-length=88 --exclude=__pycache__,venv || {
        print_warning "Avertissements de linting détectés"
    }
    
    # Formatage du code
    print_status "Vérification du formatage du code..."
    black --check . || {
        print_warning "Code non formaté détecté, exécutez 'black .' pour corriger"
    }
    
    # Type checking
    print_status "Vérification des types Python..."
    pip install mypy
    mypy . --ignore-missing-imports || {
        print_warning "Erreurs de types détectées"
    }
    
    # Tests unitaires
    print_status "Exécution des tests unitaires backend..."
    export PYTHONPATH=$PYTHONPATH:$(pwd)
    export USE_GPU=false
    export SECRET_KEY=test-secret-key
    export DATABASE_URL=sqlite:///./test.db
    
    pytest tests/ -v --cov=. --cov-report=html --cov-report=term-missing || {
        print_error "Échec des tests unitaires backend"
        return 1
    }
    
    cd ..
    print_success "Tests backend terminés avec succès"
}

# Tests E2E
run_e2e_tests() {
    print_status "Démarrage des tests E2E..."
    
    # Vérifier que les builds sont disponibles
    if [ ! -d "frontend/build" ]; then
        print_status "Build frontend non trouvé, exécution du build..."
        run_frontend_tests
    fi
    
    # Démarrer le backend
    print_status "Démarrage du serveur backend..."
    cd backend
    source ../venv/bin/activate
    export USE_GPU=false
    export SECRET_KEY=test-secret-key
    export DATABASE_URL=sqlite:///./test_e2e.db
    
    python run.py &
    BACKEND_PID=$!
    cd ..
    
    # Attendre que le backend soit prêt
    print_status "Attente du démarrage du backend..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null; then
            break
        fi
        sleep 1
    done
    
    # Démarrer le frontend
    print_status "Démarrage du serveur frontend..."
    cd frontend
    export REACT_APP_API_URL=http://localhost:8000
    
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    # Attendre que le frontend soit prêt
    print_status "Attente du démarrage du frontend..."
    for i in {1..60}; do
        if curl -s http://localhost:3000 > /dev/null; then
            break
        fi
        sleep 1
    done
    
    # Exécuter les tests Cypress
    print_status "Exécution des tests E2E..."
    cd frontend
    npx cypress run || {
        print_error "Échec des tests E2E"
        # Nettoyer les processus
        kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
        return 1
    }
    cd ..
    
    # Nettoyer les processus
    print_status "Nettoyage des processus..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    
    print_success "Tests E2E terminés avec succès"
}

# Tests de sécurité
run_security_tests() {
    print_status "Démarrage des tests de sécurité..."
    
    # Audit npm
    cd frontend
    npm audit --audit-level=high || {
        print_warning "Vulnérabilités détectées dans les dépendances frontend"
    }
    cd ..
    
    # Tests de sécurité Python
    cd backend
    source ../venv/bin/activate
    pip install safety bandit
    
    safety check || {
        print_warning "Vulnérabilités détectées dans les dépendances backend"
    }
    
    bandit -r . -f json -o bandit-report.json || {
        print_warning "Problèmes de sécurité détectés par Bandit"
    }
    cd ..
    
    print_success "Tests de sécurité terminés"
}

# Génération de rapport
generate_report() {
    print_status "Génération du rapport de tests..."
    
    REPORT_DIR="test-reports"
    mkdir -p $REPORT_DIR
    
    # Copier les rapports de couverture
    if [ -d "frontend/coverage" ]; then
        cp -r frontend/coverage $REPORT_DIR/frontend-coverage
    fi
    
    if [ -d "backend/htmlcov" ]; then
        cp -r backend/htmlcov $REPORT_DIR/backend-coverage
    fi
    
    # Copier les vidéos Cypress si elles existent
    if [ -d "frontend/cypress/videos" ]; then
        cp -r frontend/cypress/videos $REPORT_DIR/e2e-videos
    fi
    
    # Générer un rapport HTML simple
    cat > $REPORT_DIR/index.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>AestheticAI - Rapport de Tests</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .success { color: green; }
        .warning { color: orange; }
        .error { color: red; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>AestheticAI - Rapport de Tests</h1>
    <p>Généré le: $(date)</p>
    
    <div class="section">
        <h2>Couverture de Code</h2>
        <ul>
            <li><a href="frontend-coverage/lcov-report/index.html">Frontend Coverage</a></li>
            <li><a href="backend-coverage/index.html">Backend Coverage</a></li>
        </ul>
    </div>
    
    <div class="section">
        <h2>Tests E2E</h2>
        <ul>
            <li><a href="e2e-videos/">Vidéos Cypress</a></li>
        </ul>
    </div>
</body>
</html>
EOF
    
    print_success "Rapport généré dans $REPORT_DIR/"
}

# Fonction principale
main() {
    local test_type=${1:-all}
    
    print_status "Démarrage des tests AestheticAI - Type: $test_type"
    
    check_prerequisites
    
    case $test_type in
        frontend)
            run_frontend_tests
            ;;
        backend)
            run_backend_tests
            ;;
        e2e)
            run_e2e_tests
            ;;
        security)
            run_security_tests
            ;;
        all)
            run_frontend_tests
            run_backend_tests
            run_e2e_tests
            run_security_tests
            generate_report
            ;;
        *)
            print_error "Type de test invalide: $test_type"
            echo "Usage: $0 [frontend|backend|e2e|security|all]"
            exit 1
            ;;
    esac
    
    print_success "Tests terminés avec succès!"
}

# Gestion des signaux pour nettoyer en cas d'interruption
cleanup() {
    print_warning "Interruption détectée, nettoyage..."
    pkill -f "python run.py" 2>/dev/null || true
    pkill -f "npm start" 2>/dev/null || true
    exit 1
}

trap cleanup SIGINT SIGTERM

# Exécuter le script
main "$@"
