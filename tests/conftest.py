"""
conftest.py — Pytest configuration and environment setup for OptiCrop.
"""

import os
import sys

# Compute project paths
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(TESTS_DIR, ".."))
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
UTILS_DIR = os.path.join(BACKEND_DIR, "utils")
MODELS_DIR = os.path.join(BACKEND_DIR, "models")
CONFIG_DIR = os.path.join(BACKEND_DIR, "config")

# Add all relevant paths to sys.path
for p in [PROJECT_ROOT, BACKEND_DIR, UTILS_DIR, MODELS_DIR, CONFIG_DIR, TESTS_DIR]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)

# Ensure 'app' imports resolve to backend.app
if "app" not in sys.modules:
    import backend.app as backend_app
    sys.modules["app"] = backend_app
