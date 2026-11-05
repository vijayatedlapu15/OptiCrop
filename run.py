"""
run.py — OptiCrop Application Entry Point.

Starts the OptiCrop Smart Agricultural Optimization Engine.
Integrates the reorganized Frontend (templates, static) and Backend (app, models, utils, config).
"""

import os
import sys
from dotenv import load_dotenv

# Base directory paths
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
UTILS_DIR = os.path.join(BACKEND_DIR, "utils")
MODELS_DIR = os.path.join(BACKEND_DIR, "models")
CONFIG_DIR = os.path.join(BACKEND_DIR, "config")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

# Ensure all packages are on sys.path
for p in [ROOT_DIR, BACKEND_DIR, UTILS_DIR, MODELS_DIR, CONFIG_DIR]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

# Load environment configuration
load_dotenv(os.path.join(ROOT_DIR, ".env"))

# Import the configured Flask application
from backend.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    print("=" * 70)
    print(" OptiCrop - Smart Agricultural Optimization Engine")
    print("=" * 70)
    print(f" Root Directory   : {ROOT_DIR}")
    print(f" Frontend Source  : {FRONTEND_DIR}")
    print(f" Backend Source   : {BACKEND_DIR}")
    print(f" Templates        : {app.template_folder}")
    print(f" Static Assets    : {app.static_folder}")
    print(f" Server URL       : http://{host}:{port}/")
    print(" Modules Active   : Dashboard | Recommend | Suitability | Disease | Research")
    print("=" * 70)

    app.run(host=host, port=port, debug=debug)
