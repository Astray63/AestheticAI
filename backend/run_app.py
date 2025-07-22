#!/usr/bin/env python3
"""
Point d'entrée pour lancer l'application AestheticAI
Compatible avec l'ancien système et le nouveau
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire backend au PYTHONPATH
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Définir la variable d'environnement pour les modèles de test
if os.getenv("TESTING_MODE") is None:
    os.environ["TESTING_MODE"] = "false"

try:
    # Essayer d'importer la nouvelle application
    from app.main import app
    print("✅ Utilisation de la nouvelle architecture modulaire")
except ImportError:
    # Fallback vers l'ancienne application
    try:
        from main import app
        print("⚠️  Fallback vers l'ancienne architecture")
    except ImportError:
        print("❌ Impossible de charger l'application")
        sys.exit(1)

if __name__ == "__main__":
    import uvicorn
    
    # Configuration par défaut
    config = {
        "host": "0.0.0.0",
        "port": 8000,
        "reload": os.getenv("DEBUG", "false").lower() == "true",
        "log_level": "info"
    }
    
    print(f"🚀 Démarrage d'AestheticAI sur http://{config['host']}:{config['port']}")
    print(f"📚 Documentation: http://{config['host']}:{config['port']}/docs")
    
    uvicorn.run(app, **config)
