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
raw_db_url = os.getenv("DATABASE_URL") or os.getenv("AZURE_POSTGRESQL_CONNECTIONSTRING")

if raw_db_url:
    # Azure, Railway and Heroku sometimes supply postgres:// instead of postgresql://
    if raw_db_url.startswith("postgres://"):
        raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)
    
    # Azure PostgreSQL Flexible Server requires sslmode=require
    if "postgres.database.azure.com" in raw_db_url and "sslmode" not in raw_db_url:
        separator = "&" if "?" in raw_db_url else "?"
        raw_db_url = f"{raw_db_url}{separator}sslmode=require"

    DATABASE_URL = raw_db_url
else:
    # Fallback to local SQLite if DATABASE_URL is not set
    DB_FILE = DATA_DIR / "maintenance.db"
    DATABASE_URL = f"sqlite:///{DB_FILE}"

# Application Settings
APP_TITLE = os.getenv("APP_TITLE", "Stok & Makine Bakım Takip Sistemi")
APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "Yerel ağda veya bulutta (Azure / Railway) çalışan modern makine bakım ve kritik yedek parça takip platformu")
APP_VERSION = "1.0.0"

# Host & Port Settings (Azure uses WEBSITES_PORT, Railway/Containers use PORT)
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT") or os.getenv("WEBSITES_PORT") or "8000")

# Auto-seed sample data on first launch if empty
AUTO_SEED = os.getenv("AUTO_SEED", "true").lower() in ("true", "1", "yes")

# Maintenance thresholds (days)
UPCOMING_MAINTENANCE_DAYS_THRESHOLD = int(os.getenv("UPCOMING_MAINTENANCE_DAYS_THRESHOLD", "7"))
