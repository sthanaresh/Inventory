import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ==========================================
# APPLICATION SETTINGS
# ==========================================

APP_NAME = os.getenv("APP_NAME", "Inventory Management")

APP_ENV = os.getenv("APP_ENV", "development")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ==========================================
# DATABASE SETTINGS
# ==========================================

DATABASE_PATH = Path(
    os.getenv(
        "DATABASE_PATH",
        str(BASE_DIR / "InventoryManagement.db")
    )
).expanduser()

DATABASE_TIMEOUT = float(
    os.getenv("DATABASE_TIMEOUT", "30")
)

# ==========================================
# LOGGING SETTINGS
# ==========================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

LOG_DIR = Path(
    os.getenv("LOG_DIR", str(BASE_DIR / "logs"))
).expanduser()

# ==========================================
# INVENTORY SETTINGS
# ==========================================

CURRENCY = os.getenv("CURRENCY", "EUR")

DATE_FORMAT = os.getenv("DATE_FORMAT", "%d-%m-%Y")

# ==========================================
# BACKUP SETTINGS
# ==========================================

BACKUP_ENABLED = os.getenv(
    "BACKUP_ENABLED", "True"
).lower() == "true"

BACKUP_DIR = Path(
    os.getenv("BACKUP_DIR", str(BASE_DIR / "backups"))
).expanduser()

# ==========================================
# VALIDATION
# ==========================================

if DATABASE_TIMEOUT < 0:
    raise ValueError("DATABASE_TIMEOUT cannot be negative.")

if not APP_NAME.strip():
    raise ValueError("APP_NAME cannot be empty.")

if LOG_LEVEL not in {
    "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
}:
    raise ValueError("Invalid LOG_LEVEL.")

if APP_ENV not in {"development", "testing", "production"}:
    raise ValueError("Invalid APP_ENV.")
