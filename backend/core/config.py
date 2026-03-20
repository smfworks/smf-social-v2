"""Configuration management for SMF Social v2."""
import os
from pathlib import Path
from typing import Optional

# Base directories
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))

# Ensure data directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Security
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60 * 24  # 24 hours

# Encryption
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "change-me-in-production-32-char-key!!")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/smf_social.db")

# Frontend URL (for OAuth callbacks)
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

# API Settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Scheduler
SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"

# Debug
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
