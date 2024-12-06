from PyQt5.QtCore import QObject, pyqtSignal
import zipfile
import os
import shutil
from config import logger

DELETE_TARGETS = {
    "Lethal Company": {
        "folder": os.path.join(os.getenv("PROGRAMFILES(X86)"), "Steam", "steamapps", "common", "Lethal Company", "BepInEx"),
        "files": [
            os.path.join(os.getenv("PROGRAMFILES(X86)"), "Steam", "steamapps", "common", "Lethal Company", "doorstop_config.ini"),
            os.path.join(os.getenv("PROGRAMFILES(X86)"), "Steam", "steamapps", "common", "Lethal Company", "winhttp.dll")
        ]
    },
    "Elden Ring": {
        "folder": os.path.join(os.getenv("PROGRAMFILES(X86)"), "Steam", "steamapps", "common", "Elden Ring", "Backup"),
        "files": [
            os.path.join(os.getenv("PROGRAMFILES(X86)"), "Steam", "steamapps", "common", "Elden Ring", "settings.ini"),
            os.path.join(os.getenv("PROGRAMFILES(X86)"), "Steam", "steamapps", "common", "Elden Ring", "notes.txt")
        ]
    }
}

class PatchExtractor(QObject):
    """Handles patch extraction with progress tracking."""
    progress = pyqtSignal(int)

    def extract_patch(self, zip_path, target_path):
        if not os.path.exists(zip_path):
            logger.critical("Patch file not found.")
            raise FileNotFoundError("Patch file not found.")

        if not os.path.exists(target_path):
            os.makedirs(target_path)
            logger.info(f"Created target directory: {target_path}")

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                total_files = len(zip_ref.namelist())
                for index, file in enumerate(zip_ref.namelist(), start=1):
                    zip_ref.extract(file, target_path)
                    progress = int((index / total_files) * 100)
                    self.progress.emit(progress)
                logger.info(f"Successfully unpacked patch to {target_path}")
        except Exception as e:
            logger.error(f"Error unpacking patch: {e}")
            raise RuntimeError(f"Error unpacking patch: {e}")

def delete_old_data(game_name):
    """Deletes old game data based on predefined targets."""
    if game_name not in DELETE_TARGETS:
        logger.error(f"No delete targets defined for {game_name}.")
        raise ValueError(f"No delete targets defined for {game_name}.")

    targets = DELETE_TARGETS[game_name]

    folder = targets.get("folder")
    if folder and os.path.exists(folder):
        try:
            shutil.rmtree(folder)
            logger.info(f"Deleted folder: {folder}")
        except Exception as e:
            logger.error(f"Error deleting folder {folder}: {e}")
        else:
            logger.info(f"Folder {folder} did not exist.")

    for file_path in targets.get("files", []):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")
        else:
            logger.info(f"File {file_path} did not exist.")

def apply_patch(zip_path, target_path):
    if not os.path.exists(zip_path):
        logger.critical("Patch file not found.")
        raise FileNotFoundError("Patch file not found.")

    if not os.path.exists(target_path):
        logger.critical("Target path does not exist.")
        raise FileNotFoundError("Target path does not exist.")

    try:
        shutil.unpack_archive(zip_path, target_path)
        logger.info(f"Successfully unpacked patch to {target_path}")
    except Exception as e:
        logger.error(f"Error unpacking patch: {e}")
        raise RuntimeError(f"Error unpacking patch: {e}")
