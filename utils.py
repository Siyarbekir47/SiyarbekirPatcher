import sys
import os

import requests
from config import logger

def check_for_updates(version_url: str, current_version: str):
    try:
        response = requests.get(version_url, timeout=5)
        response.raise_for_status()
        data = response.json()
        remote_version = data.get("version")
        download_url = data.get("download_url")

        if remote_version and download_url:
            # Sehr einfacher Vergleich:
            if remote_version > current_version:
                logger.info(f"Neue Version verfügbar: {remote_version}")
                return True, remote_version, download_url
            else:
                logger.info("Keine neuere Version verfügbar.")
                return False, current_version, None
        else:
            logger.warning("Versions-JSON unvollständig oder keys fehlen.")
            return False, current_version, None

    except Exception as e:
        logger.error(f"Fehler beim Prüfen auf Updates: {e}")
        return False, current_version, None

def resource_path(relative_path: str) -> str:

    if hasattr(sys, '_MEIPASS'):  # Falls als .exe durch PyInstaller ausgeführt
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)  # Entwicklungsmodus
