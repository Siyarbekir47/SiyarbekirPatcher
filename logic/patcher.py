from PyQt5.QtCore import QObject, pyqtSignal
import zipfile
import os
import shutil
from config import logger, APP_IDS, DELETE_TARGETS

class PatchExtractor(QObject):
    """Handles patch extraction with progress tracking."""
    progress = pyqtSignal(int)

    def extract_patch(self, zip_path: str, target_path: str) -> None:
        if not os.path.exists(zip_path):
            logger.critical("Patch file not found.")
            raise FileNotFoundError("Patch file not found.")

        if not os.path.exists(target_path):
            os.makedirs(target_path)
            logger.info(f"Created target directory: {target_path}")

        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                files = zip_ref.namelist()
                total_files = len(files)
                for index, file in enumerate(files, start=1):
                    zip_ref.extract(file, target_path)
                    progress = int((index / total_files) * 100)
                    self.progress.emit(progress)
                logger.info(f"Successfully unpacked patch to {target_path}")
        except Exception as e:
            logger.error(f"Error unpacking patch: {e}")
            raise RuntimeError(f"Error unpacking patch: {e}")


def delete_old_data(game_name: str, base_path: str) -> None:
    if not base_path:
        logger.error(f"Game path for {game_name} could not be determined.")
        raise ValueError(f"Game path for {game_name} could not be determined.")

    if game_name not in DELETE_TARGETS:
        logger.error(f"No delete targets defined for {game_name}.")
        raise ValueError(f"No delete targets defined for {game_name}.")

    game_targets = DELETE_TARGETS[game_name]
    folder_name = game_targets.get("folder")
    files = game_targets.get("files", [])

    # Ordner löschen
    if folder_name:
        folder_path = os.path.join(base_path, folder_name)
        if os.path.exists(folder_path):
            try:
                shutil.rmtree(folder_path)
                logger.info(f"Deleted folder: {folder_path}")
            except Exception as e:
                logger.error(f"Error deleting folder {folder_path}: {e}")

    # Dateien löschen
    for relative_file_path in files:
        file_path = os.path.join(base_path, relative_file_path)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Error deleting file {file_path}: {e}")
        else:
            logger.info(f"File {file_path} did not exist.")


def apply_patch(zip_path: str, target_path: str) -> None:
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
