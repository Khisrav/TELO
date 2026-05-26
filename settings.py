import json
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Mon–Fri 9–20, Sat 10–18, Sun closed (hour integers, end exclusive)
WORKING_HOURS = [
    (9, 20),
    (9, 20),
    (9, 20),
    (9, 20),
    (9, 20),
    (10, 18),
    None,
]


def _require(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _int_env(name: str, default: int | None = None) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        if default is None:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return default
    return int(raw)


BOT_TOKEN = _require("BOT_TOKEN")

SPECIALIST_TG_ID = _int_env("SPECIALIST_TG_ID")
SPECIALIST_PHONE = os.getenv("SPECIALIST_PHONE", "").strip()
ADMIN_TELEGRAM_ID = _int_env("ADMIN_TELEGRAM_ID")

GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL", "").strip()
SMSRU_API = os.getenv("SMSRU_API", "").strip()

DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "bookings.db"))
)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

START_PHOTO = Path(os.getenv("START_PHOTO", str(BASE_DIR / "assets" / "karina.jpg")))
ABOUT_PHOTO = Path(os.getenv("ABOUT_PHOTO", str(BASE_DIR / "assets" / "karina_about.jpg")))

REDIS_URL = os.getenv("REDIS_URL", "").strip()
HEALTH_PORT = int(os.getenv("PORT", "8080"))


def google_credentials_dict() -> dict | None:
    raw = os.getenv("GOOGLE_CREDENTIALS_JSON", "").strip()
    if not raw:
        return None
    return json.loads(raw)
