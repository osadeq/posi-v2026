"""
Configuration de l'application Flask
"""
import os
from pathlib import Path

import shutil

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
BD_DIR = DATA_DIR / "bd"

# Check if running on Vercel
IS_VERCEL = os.environ.get('VERCEL') == '1'
WRITABLE_DIR = Path("/tmp/posidata") if IS_VERCEL else DATA_DIR

UPLOAD_DIR = WRITABLE_DIR / "upload"
EXPORT_DIR = WRITABLE_DIR / "export"
CANDIDATS_DIR = WRITABLE_DIR / "candidats"
ARCHIVES_DIR = WRITABLE_DIR / "archives"
ARCHIVES_CANDIDATS_DIR = ARCHIVES_DIR / "candidats"

# Ensure directories exist
WRITABLE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
ARCHIVES_CANDIDATS_DIR.mkdir(parents=True, exist_ok=True)
CANDIDATS_DIR.mkdir(parents=True, exist_ok=True)

# Flask config
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-posi-2026')
DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'

# Infos de l'application
APP_VERSION = "2026.3.1"
LAST_UPDATE = "23 Mars 2026"

# File upload config
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
ALLOWED_EXTENSIONS = {'csv', 'txt', 'xlsx'}

# Data files
QUESTIONS_FILE = BD_DIR / "00_questions.json"
PROGRAMMES_FILE = BD_DIR / "01_programmes.json"

if IS_VERCEL:
    CANDIDATS_FILE = WRITABLE_DIR / "03_candidats.json"
    if not CANDIDATS_FILE.exists() and (BD_DIR / "03_candidats.json").exists():
        shutil.copy2(BD_DIR / "03_candidats.json", CANDIDATS_FILE)
    if (DATA_DIR / "candidats").exists():
        for item in (DATA_DIR / "candidats").iterdir():
            if item.is_dir() and not (CANDIDATS_DIR / item.name).exists():
                shutil.copytree(item, CANDIDATS_DIR / item.name)
else:
    CANDIDATS_FILE = BD_DIR / "03_candidats.json"

# Pagination
ITEMS_PER_PAGE = 20
