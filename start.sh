#!/bin/bash

# 🚀 Script de démarrage rapide pour AestheticAI
# Usage: ./start.sh [dev|prod|stop|logs|clean|health]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_message() {
    echo -e "${BLUE}[AestheticAI]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ [SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  [WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}❌ [ERROR]${NC} $1"
}

print_info() {
    echo -e "${PURPLE}ℹ️  [INFO]${NC} $1"
}

# Vérifier si Docker est installé
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé. Veuillez l'installer d'abord."
        print_info "Installation: https://docs.docker.com/get-docker/"
        exit 1
    fi

    # Vérifier docker compose (v2) ou docker-compose (v1)
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    else
        print_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
        print_info "Installation: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

# Fonction d'aide améliorée
show_help() {
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commandes disponibles:"
    echo "  dev       - Démarrer en mode développement (avec hot reload)"
    echo "  prod      - Démarrer en mode production"
    echo "  stop      - Arrêter tous les services"
    echo "  restart   - Redémarrer tous les services"
    echo "  logs      - Afficher les logs en temps réel"
    echo "  build     - Construire les images Docker"
    echo "  clean     - Nettoyer les containers et volumes"
    echo "  status    - Afficher le statut des services"
    echo "  help      - Afficher cette aide"
    echo ""
    echo "Options:"
    echo "  --no-cache    - Reconstruire sans utiliser le cache"
    echo "  --verbose     - Affichage verbeux"
    echo ""
    echo "Exemples:"
    echo "  $0 dev                 # Démarrer en mode développement"
    echo "  $0 prod --no-cache     # Démarrer en prod en reconstruisant"
    echo "  $0 logs backend        # Voir les logs du backend"
}

# Démarrer en mode développement
start_dev() {
    print_message "Démarrage d'AestheticAI en mode développement..."
    
    if [[ "$*" == *"--no-cache"* ]]; then
        print_message "Construction des images sans cache..."
        $DOCKER_COMPOSE -f docker-compose.dev.yml build --no-cache
    fi
    
    $DOCKER_COMPOSE -f docker-compose.dev.yml up -d
    
    print_success "Services démarrés en mode développement!"
    print_message "Frontend: http://localhost:3000"
    print_message "Backend API: http://localhost:8000"
    print_message "Documentation API: http://localhost:8000/docs"
    print_message "Database: localhost:5432"
    
    print_message "Utilisez '$DOCKER_COMPOSE -f docker-compose.dev.yml logs -f' pour voir les logs"
}

# Démarrer en mode production
start_prod() {
    print_message "Démarrage d'AestheticAI en mode production..."
    
    if [[ "$*" == *"--no-cache"* ]]; then
        print_message "Construction des images sans cache..."
        $DOCKER_COMPOSE build --no-cache
    fi
    
    $DOCKER_COMPOSE up -d
    
    print_success "Services démarrés en mode production!"
    print_message "Application: http://localhost:80"
    print_message "API Backend: http://localhost:80/api"
    print_message "Documentation API: http://localhost:80/docs"
    
    print_message "Utilisez '$DOCKER_COMPOSE logs -f' pour voir les logs"
}

# Arrêter les services
stop_services() {
    print_message "Arrêt des services..."
    $DOCKER_COMPOSE down 2>/dev/null || true
    $DOCKER_COMPOSE -f docker-compose.dev.yml down 2>/dev/null || true
    print_success "Services arrêtés!"
}

# Redémarrer les services
restart_services() {
    print_message "Redémarrage des services..."
    stop_services
    sleep 2
    if [[ -f "docker-compose.dev.yml" ]] && docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
        start_dev
    else
        start_prod
    fi
}

# Afficher les logs
show_logs() {
    if [[ -n "$2" ]]; then
        # Service spécifique
        if $DOCKER_COMPOSE ps | grep -q "Up"; then
            $DOCKER_COMPOSE logs -f "$2"
        elif $DOCKER_COMPOSE -f docker-compose.dev.yml ps | grep -q "Up"; then
            $DOCKER_COMPOSE -f docker-compose.dev.yml logs -f "$2"
        else
            print_error "Aucun service en cours d'exécution"
        fi
    else
        # Tous les services
        if $DOCKER_COMPOSE ps | grep -q "Up"; then
            $DOCKER_COMPOSE logs -f
        elif $DOCKER_COMPOSE -f docker-compose.dev.yml ps | grep -q "Up"; then
            $DOCKER_COMPOSE -f docker-compose.dev.yml logs -f
        else
            print_error "Aucun service en cours d'exécution"
        fi
    fi
}

# Construire les images
build_images() {
    print_message "Construction des images Docker..."
    
    if [[ "$*" == *"--no-cache"* ]]; then
        $DOCKER_COMPOSE build --no-cache
        $DOCKER_COMPOSE -f docker-compose.dev.yml build --no-cache
    else
        $DOCKER_COMPOSE build
        $DOCKER_COMPOSE -f docker-compose.dev.yml build
    fi
    
    print_success "Images construites avec succès!"
}

# Nettoyer
clean_all() {
    print_warning "Cette opération va supprimer tous les containers, images et volumes liés à AestheticAI."
    read -p "Êtes-vous sûr ? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_message "Nettoyage en cours..."
        
        # Arrêter tous les services
        $DOCKER_COMPOSE down -v 2>/dev/null || true
        $DOCKER_COMPOSE -f docker-compose.dev.yml down -v 2>/dev/null || true
        
        # Supprimer les images
        docker rmi $(docker images | grep aesthetic | awk '{print $3}') 2>/dev/null || true
        
        # Nettoyer les volumes orphelins
        docker volume prune -f
        
        print_success "Nettoyage terminé!"
    else
        print_message "Nettoyage annulé."
    fi
}

# Afficher le statut
show_status() {
    print_message "Statut des services AestheticAI:"
    echo ""
    
    echo "=== Mode Production ==="
    if $DOCKER_COMPOSE ps 2>/dev/null | grep -q "Up"; then
        $DOCKER_COMPOSE ps
    else
        echo "Aucun service en mode production"
    fi
    
    echo ""
    echo "=== Mode Développement ==="
    if $DOCKER_COMPOSE -f docker-compose.dev.yml ps 2>/dev/null | grep -q "Up"; then
        $DOCKER_COMPOSE -f docker-compose.dev.yml ps
    else
        echo "Aucun service en mode développement"
    fi
}

# Script principal
main() {
    check_docker
    
    case "${1:-help}" in
        "dev")
            start_dev "$@"
            ;;
        "prod")
            start_prod "$@"
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            show_logs "$@"
            ;;
        "build")
            build_images "$@"
            ;;
        "clean")
            clean_all
            ;;
        "status")
            show_status
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Commande inconnue: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# Exécuter le script
main "$@"
