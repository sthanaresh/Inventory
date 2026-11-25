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

# ==========================================
# DATABASE SETTINGS
# ==========================================

DATABASE_PATH = Path(
    os.getenv(
        "DATABASE_PATH",
        str(BASE_DIR / "InventoryManagement.db")
    )
).expanduser()
