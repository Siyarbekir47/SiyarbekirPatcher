import winreg
import os
from config import logger

def find_steam_game_path(app_id):
    """Finds the installation path of a Steam game by app ID."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Wow6432Node\\Valve\\Steam") as key:
            steam_install_path, _ = winreg.QueryValueEx(key, "InstallPath")

        # Find libraryfolders.vdf
        library_file = os.path.join(steam_install_path, "steamapps", "libraryfolders.vdf")
        if not os.path.exists(library_file):
            logger.error("libraryfolders.vdf not found.")
            raise FileNotFoundError("libraryfolders.vdf not found.")

        # Parse libraryfolders.vdf
        with open(library_file, "r", encoding="utf-8") as file:
            content = file.read()
        libraries = parse_libraryfolders_vdf(content)

        # Find the app ID in libraries
        for library_path in libraries.values():
            game_path = os.path.join(library_path, "steamapps", "common", "Lethal Company")
            game_path = os.path.normpath(game_path)  # Normalize path
            if os.path.exists(game_path):
                logger.info(f"Found game path: {game_path}")
                return game_path

        logger.error(f"Game path for app ID {app_id} not found in any Steam library.")
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return None

def parse_libraryfolders_vdf(content):
    """Parses libraryfolders.vdf to extract Steam library paths."""
    libraries = {}
    lines = content.splitlines()
    current_path = None

    for line in lines:
        line = line.strip()
        if line.startswith('"path"'):
            parts = line.split('"')
            if len(parts) >= 4:
                current_path = os.path.normpath(parts[3])  # Normalize path
        elif current_path and line.startswith('"apps"'):
            continue
        elif current_path and line.startswith('"') and '"' in line:
            parts = line.split('"')
            if len(parts) >= 4:
                app_id = parts[1]
                if app_id.isdigit():
                    libraries[app_id] = current_path

    logger.debug(f"Parsed library folders: {libraries}")
    return libraries
