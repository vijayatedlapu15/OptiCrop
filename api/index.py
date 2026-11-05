"""
api/index.py — Vercel Serverless Function Entry Point for OptiCrop.

Exposes the WSGI Flask application object (`app`) for Vercel's Python runtime.
Configures system path to reliably locate backend modules, config, and ML models.
"""

import os
import sys

# Compute project root and backend directories
API_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(API_DIR, ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

# Ensure all packages are on sys.path
for p in [
    PROJECT_ROOT,
    BACKEND_DIR,
    os.path.join(BACKEND_DIR, "utils"),
    os.path.join(BACKEND_DIR, "models"),
    os.path.join(BACKEND_DIR, "config")
]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

# Import the configured Flask application
from backend.app import app
