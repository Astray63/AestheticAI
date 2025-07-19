#!/usr/bin/env python3
"""
Point d'entrée pour l'application AestheticAI Backend
"""

if __name__ == "__main__":
    import uvicorn
    from main import app

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
