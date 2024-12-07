import sys
import requests
import subprocess
from PyQt5.QtWidgets import QMessageBox
from config import logger, CURRENT_VERSION
from utils import check_for_updates

def check_and_prompt_update(version_url: str) -> None:
    is_update_available, new_version, download_url = check_for_updates(version_url, CURRENT_VERSION)
    if is_update_available:
        reply = QMessageBox.question(
            None,
            "Update verfügbar",
            f"Eine neue Version ({new_version}) ist verfügbar. Jetzt aktualisieren?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            perform_update(download_url)
    else:
        logger.info("Keine neuere Version verfügbar. Weiter mit aktueller Version.")

def perform_update(download_url: str) -> None:
    zip_filename = "patcherupdate.zip"
    try:
        logger.info("Update wird heruntergeladen...")
        r = requests.get(download_url, stream=True, timeout=10)
        r.raise_for_status()
        with open(zip_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info("Update erfolgreich heruntergeladen.")

        batch_content = r"""@echo off
cd /d "%~dp0"

echo Warte 2 Sekunden, um sicherzugehen, dass die Anwendung beendet ist...
timeout /t 2 /nobreak >nul

echo Entpacke Update...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -Force 'patcherupdate.zip' '.'"
if %errorlevel% neq 0 (
    echo Fehler beim Entpacken. Stelle sicher, dass patcherupdate.zip vorhanden und nicht beschaedigt ist.
    pause
    exit /b 1
)

echo Loesche Update-Archiv (patcherupdate.zip)...
del /f /q "patcherupdate.zip"

echo Loesche diese Batch-Datei nach 2 Sekunden...
start "" cmd /c "timeout /t 2 >nul & del /f /q \"%~f0\""

echo Update abgeschlossen.
exit
"""

        with open("update.bat", "w", encoding="utf-8") as bf:
            bf.write(batch_content)
        logger.info("update.bat erstellt.")

        # update.bat starten
        subprocess.Popen(["cmd", "/c", "update.bat"], shell=True)

        # Anwendung normal beenden
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fehler beim Herunterladen des Updates: {e}")
        QMessageBox.critical(None, "Update fehlgeschlagen", f"Fehler beim Download: {e}")
        # Anwendung läuft einfach weiter
