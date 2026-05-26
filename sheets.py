import logging
from pathlib import Path

import gspread
from oauth2client.service_account import ServiceAccountCredentials

from settings import BASE_DIR, GOOGLE_SHEET_URL, google_credentials_dict

logger = logging.getLogger(__name__)

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

CREDENTIALS_FILE = BASE_DIR / "credentials.json"


def _get_credentials():
    creds_dict = google_credentials_dict()
    if creds_dict:
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)

    if CREDENTIALS_FILE.is_file():
        return ServiceAccountCredentials.from_json_keyfile_name(str(CREDENTIALS_FILE), SCOPE)

    return None


def _get_sheet():
    if not GOOGLE_SHEET_URL:
        return None

    try:
        creds = _get_credentials()
        if creds is None:
            logger.warning("Google Sheets credentials not configured")
            return None
        gc = gspread.authorize(creds)
        return gc.open_by_url(GOOGLE_SHEET_URL).sheet1
    except Exception:
        logger.exception("Failed to connect to Google Sheets")
        return None


def ensure_headers():
    sh = _get_sheet()
    if sh is None:
        return

    try:
        if not sh.row_values(1):
            sh.append_row([
                "ID", "Имя", "Username", "Телефон", "Коллекция",
                "Услуга", "Цена", "Длительность", "Дата", "Время",
                "Статус", "Создано",
            ])
    except Exception:
        logger.exception("Failed to create sheet headers")


def append_booking(b: dict):
    sh = _get_sheet()
    if sh is None:
        return

    try:
        sh.append_row([
            b.get("id"), b.get("full_name"), b.get("username"),
            b.get("phone"), b.get("category"), b.get("service"),
            b.get("price"), b.get("duration"), b.get("date"),
            b.get("time"), b.get("status"), b.get("created_at"),
        ])
    except Exception:
        logger.exception("Failed to append booking to sheet")


def update_status(bid: int, status: str):
    sh = _get_sheet()
    if sh is None:
        return

    try:
        col = sh.col_values(1)
        bid_str = str(bid)
        if bid_str in col:
            row = col.index(bid_str) + 1
            sh.update_cell(row, 11, status)
    except Exception:
        logger.exception("Failed to update booking status in sheet")
