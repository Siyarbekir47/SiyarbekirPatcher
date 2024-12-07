import sys
import os
import subprocess
import requests
from PyQt5.QtWidgets import QMessageBox
from config import logger, CURRENT_VERSION
from utils import check_for_updates

def perform_update(new_version: str, download_url: str) -> None:
    zip_filename = f"patcherupdate.zip"
    try:
        logger.info("Update wird heruntergeladen...")
        r = requests.get(download_url, stream=True, timeout=10)
        r.raise_for_status()

        with open(zip_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info("Update erfolgreich heruntergeladen.")

        # Batch-Datei erstellen
        batch_content = f"""@echo off
echo Warte auf Beenden der Anwendung...
:wait
tasklist | findstr /i "SiyarsPatcher.exe" >nul
if %errorlevel%==0 (
    echo Anwendung läuft noch, warte 1 Sekunde...
    timeout /t 1 /nobreak >nul
    goto wait
)

echo Anwendung beendet, versuche alte EXE umzubenennen...
:rename_try
rename SiyarsPatcher.exe SiyarsPatcher.old
if %errorlevel%==0 (
    echo Alte EXE erfolgreich umbenannt.
) else (
    echo Konnte alte EXE nicht umbenennen, warte 2 Sekunden und versuche erneut...
    timeout /t 2 /nobreak >nul
    goto rename_try
)

echo Entpacke jetzt das Update-Archiv...
powershell -Command "Expand-Archive -Force 'patcherupdate.zip' '.'"

echo Update entpackt.
echo Warte 5 Sekunden, um sicherzustellen, dass alle Ressourcen freigegeben sind...
timeout /t 5 /nobreak >nul

echo Lösche alte EXE (SiyarsPatcher.old)...
del SiyarsPatcher.old

echo Lösche Update-Archiv (patcherupdate.zip)...
del "patcherupdate.zip"

echo Lösche diese Batch-Datei nach 2 Sekunden...
start "" cmd /c "ping 127.0.0.1 -n 2 >nul && del \"%~f0\""

echo Starte neue Version...
start "" "%~dp0SiyarsPatcher.exe"

echo Update abgeschlossen.
exit
"""

        with open("update.bat", "w", encoding="utf-8") as bf:
            bf.write(batch_content)
        logger.info("update.bat erstellt.")

        # Batch-Datei starten
        subprocess.Popen(["cmd", "/c", "update.bat"], shell=True)

        # Anwendung beenden
        sys.exit(0)

    except Exception as e:
        logger.error(f"Fehler beim Herunterladen oder Durchführen des Updates: {e}")
        QMessageBox.critical(None, "Update fehlgeschlagen", f"Fehler beim Download oder Update: {e}")
        # Wenn hier ein Fehler auftritt, bleibt die Anwendung einfach weiter geöffnet.

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
            perform_update(new_version, download_url)
    else:
        logger.info("Wir bleiben bei der aktuellen Version.")
