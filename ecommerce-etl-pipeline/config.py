"""
Configuration module for the E-Commerce ETL Pipeline.

Manages database connection settings, file paths, and logging
configuration. All values can be overridden via environment variables.
"""

import os
from pathlib import Path

# ── Base Directory ──────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent

# ── Data Directories ───────────────────────────────────────
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
CLEANED_DATA_DIR = BASE_DIR / "data" / "cleaned"
LOG_DIR = BASE_DIR / "logs"
SQL_DIR = BASE_DIR / "sql"

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, CLEANED_DATA_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ── PostgreSQL Connection Settings ─────────────────────────
# Override these via environment variables for production use
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "ecommerce_analytics"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

# SQLAlchemy connection string (used by Jupyter notebook)
SQLALCHEMY_URI = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# ── CSV File Paths ─────────────────────────────────────────
CSV_FILES = {
    "customers": RAW_DATA_DIR / "customers.csv",
    "products": RAW_DATA_DIR / "products.csv",
    "orders": RAW_DATA_DIR / "orders.csv",
}

# ── Logging Configuration ─────────────────────────────────
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE = LOG_DIR / "pipeline.log"
