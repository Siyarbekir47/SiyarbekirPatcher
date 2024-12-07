import winreg
import os
from typing import Dict, Optional
from config import logger


def find_steam_game_path(app_id: str) -> Optional[str]:
    """
    Findet den Installationspfad eines Steam-Spiels anhand seiner App-ID.

    Ablauf:
    1. Ermittelt den Steam-Hauptinstallationspfad über die Windows-Registry.
    2. Liest die libraryfolders.vdf, um alle Steam-Bibliotheksverzeichnisse zu erhalten.
    3. Sucht in diesen Verzeichnissen nach dem spezifischen Spieleordner (hier: "Lethal Company").

    :param app_id: Die Steam-App-ID des Spiels.
    :return: Der absolute Pfad zum Spielverzeichnis, oder None, wenn nichts gefunden wurde.
    :raises FileNotFoundError: Wenn libraryfolders.vdf nicht gefunden wird.
    """
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Wow6432Node\\Valve\\Steam") as key:
            steam_install_path, _ = winreg.QueryValueEx(key, "InstallPath")
    except FileNotFoundError:
        logger.error("Steam-Installationspfad nicht in der Registry gefunden.")
        return None
    except OSError as e:
        logger.error(f"Fehler beim Zugriff auf die Registry: {e}")
        return None

    # Pfad zur libraryfolders.vdf ermitteln
    library_file = os.path.join(steam_install_path, "steamapps", "libraryfolders.vdf")
    if not os.path.exists(library_file):
        logger.error("libraryfolders.vdf not found.")
        return None

    # Bibliotheken einlesen
    try:
        with open(library_file, "r", encoding="utf-8") as file:
            content = file.read()
        libraries = parse_libraryfolders_vdf(content)
    except FileNotFoundError:
        logger.error("libraryfolders.vdf not found.")
        return None
    except Exception as e:
        logger.error(f"Unerwarteter Fehler beim Lesen von libraryfolders.vdf: {e}")
        return None

    # Im Moment ist das Spielverzeichnis noch auf "Lethal Company" festgelegt.
    # Möchtest du es dynamisch machen, kannst du den Spieleordner als Parameter übergeben oder aus config.py holen.
    game_folder_name = "Lethal Company"

    # Nach dem Spielpfad in allen Bibliotheken suchen
    for library_path in libraries.values():
        game_path = os.path.join(library_path, "steamapps", "common", game_folder_name)
        game_path = os.path.normpath(game_path)  # Pfad normalisieren
        if os.path.exists(game_path):
            logger.info(f"Found game path: {game_path}")
            return game_path

    logger.error(f"Game path for app ID {app_id} not found in any Steam library.")
    return None


def parse_libraryfolders_vdf(content: str) -> Dict[str, str]:
    """
    Parst den Inhalt der libraryfolders.vdf, um die Pfade zu allen Steam-Bibliotheken zu extrahieren.

    Die Datei libraryfolders.vdf enthält Einträge in folgender Art:
    "0"
    {
        "path" "C:\\Program Files (x86)\\Steam"
        "apps"
        {
            "12345" "SomeApp"
        }
    }
    "1"
    {
        "path" "D:\\SteamLibrary"
        "apps"
        {
            "67890" "AnotherApp"
        }
    }

    :param content: Der Textinhalt der libraryfolders.vdf.
    :return: Ein Dictionary {app_id: library_path}, wobei app_id die App-ID und library_path der Pfad zur Bibliothek ist.
    """
    libraries = {}
    lines = content.splitlines()
    current_path = None

    for line in lines:
        line = line.strip()
        if line.startswith('"path"'):
            parts = line.split('"')
            if len(parts) >= 4:
                # Extrahiere den Bibliothekspfad
                current_path = os.path.normpath(parts[3])
        elif current_path and line.startswith('"apps"'):
            # Dies ist der Beginn eines "apps" Blocks, wir ignorieren nur die Zeile
            continue
        elif current_path and line.startswith('"') and '"' in line:
            parts = line.split('"')
            if len(parts) >= 4:
                app_id = parts[1]
                if app_id.isdigit():
                    libraries[app_id] = current_path

    logger.debug(f"Parsed library folders: {libraries}")
    return libraries
