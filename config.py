"""
Configuration de l'application Flask
"""
import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BD_DIR = DATA_DIR / "bd"
UPLOAD_DIR = DATA_DIR / "upload"
EXPORT_DIR = DATA_DIR / "export"
CANDIDATS_DIR = DATA_DIR / "candidats"
ARCHIVES_DIR = DATA_DIR / "archives"
ARCHIVES_CANDIDATS_DIR = ARCHIVES_DIR / "candidats"

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVES_CANDIDATS_DIR.mkdir(parents=True, exist_ok=True)

# Flask config
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-posi-2026')
DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

# Infos de l'application
APP_VERSION = "2026.3.1"
LAST_UPDATE = "23 Mars 2026"

# File upload config
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'csv', 'txt'}

# Data files
QUESTIONS_FILE = BD_DIR / "00_questions.json"
PROGRAMMES_FILE = BD_DIR / "01_programmes.json"
CANDIDATS_FILE = BD_DIR / "03_candidats.json"

# Pagination
ITEMS_PER_PAGE = 20
