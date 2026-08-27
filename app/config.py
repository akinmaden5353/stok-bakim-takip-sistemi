import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directories
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env if present
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Database Configuration (PostgreSQL / SQLite fallback)
raw_db_url = os.getenv("DATABASE_URL")

if raw_db_url:
    # Railway and Heroku sometimes supply postgres:// instead of postgresql://
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    DATABASE_URL = raw_db_url
else:
    # Fallback to local SQLite if DATABASE_URL is not set
    DB_FILE = DATA_DIR / "maintenance.db"
    DATABASE_URL = f"sqlite:///{DB_FILE}"

# Application Settings
APP_TITLE = os.getenv("APP_TITLE", "Stok & Makine Bakım Takip Sistemi")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Yerel ağda veya bulutta çalışan modern makine bakım ve kritik yedek parça takip platformu")
APP_VERSION = "1.0.0"

# Host & Port Settings (Railway dynamically injects $PORT)
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# Auto-seed sample data on first launch if empty
AUTO_SEED = os.getenv("AUTO_SEED", "true").lower() in ("true", "1", "yes")

# Maintenance thresholds (days)
UPCOMING_MAINTENANCE_DAYS_THRESHOLD = int(os.getenv("UPCOMING_MAINTENANCE_DAYS_THRESHOLD", "7"))
