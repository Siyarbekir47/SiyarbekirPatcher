
import winreg
import os
from config import logger

def find_steam_game_path(app_id):
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Valve\Steam") as key:
            steam_install_path, _ = winreg.QueryValueEx(key, "InstallPath")

        library_file = os.path.join(steam_install_path, "steamapps", "libraryfolders.vdf")
        if not os.path.exists(library_file):
            logger.error("libraryfolders.vdf not found.")
            raise FileNotFoundError("libraryfolders.vdf not found.")

        with open(library_file, "r") as file:
            content = file.read()
            libraries = parse_libraryfolders_vdf(content)

        if app_id in libraries:
            library_path = libraries[app_id]
            game_path = os.path.join(library_path, "steamapps", "common", "Lethal Company")
            logger.info(f"Found game path: {game_path}")
            return os.path.normpath(game_path)

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

    return None

def parse_libraryfolders_vdf(content):
    libraries = {}
    lines = content.splitlines()
    current_path = None

    for line in lines:
        line = line.strip()
        if line.startswith('"path"'):
            parts = line.split('"')
            if len(parts) >= 4:
                current_path = parts[3]
        elif line.startswith('"apps"'):
            current_apps = {}
        elif current_path and line.startswith('"') and '"' in line:
            parts = line.split('"')
            if len(parts) >= 4:
                app_id = parts[1]
                if app_id.isdigit():
                    libraries[app_id] = current_path

    logger.debug(f"Parsed library folders: {libraries}")
    return libraries
