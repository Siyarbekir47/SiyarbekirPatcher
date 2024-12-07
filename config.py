import logging
CURRENT_VERSION = "1.2.2"
VERSION_URL = "https://siyarbekir.de/downloads/patcherversion.json"
# App-IDs für verschiedene Spiele
APP_IDS = {
    "Lethal Company": "1966720",
    "Elden Ring": "1245620",
}
# Hier definieren wir, welche Ordner und Dateien vor dem Patchen gelöscht werden sollen.
# Du kannst hier beliebig weitere Spiele hinzufügen oder bestehende ändern.
# Die Pfade sind relativ zum Spieleverzeichnis.
DELETE_TARGETS = {
    "Lethal Company": {
        "folder": "BepInEx",
        "files": [
            "doorstop_config.ini",
            "winhttp.dll",
        ],
    },
    "Elden Ring": {
        "folder": "Backup",
        "files": [
            "settings.ini",
            "notes.txt",
        ],
    },
}

# Logger-Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
