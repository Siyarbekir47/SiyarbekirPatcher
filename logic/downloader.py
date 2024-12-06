from PyQt5.QtCore import QThread, pyqtSignal
import requests
from config import APP_IDS, logger

class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, game_name, save_path):
        super().__init__()
        self.game_name = game_name
        self.save_path = save_path

    def run(self):
        if self.game_name not in APP_IDS:
            self.error.emit(f"No App ID found for game: {self.game_name}")
            return

        app_id = APP_IDS[self.game_name]
        zip_url = f"https://siyarbekir.de/downloads/{app_id}.zip"

        try:
            logger.info(f"Starting download for {self.game_name} from {zip_url}")
            response = requests.get(zip_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(self.save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        progress = int((downloaded_size / total_size) * 100)
                        self.progress.emit(progress)

            logger.info(f"Download successful: {self.save_path}")
            self.finished.emit(self.save_path)
        except Exception as e:
            logger.error(f"Download failed for {self.game_name}: {e}")
            self.error.emit(str(e))
