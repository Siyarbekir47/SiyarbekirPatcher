import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QVBoxLayout, QPushButton, QLabel, QWidget, QMessageBox,
    QApplication, QStyle, QProgressBar, QFileDialog
)
from PyQt5.QtGui import QFont, QPixmap
from config import APP_IDS, logger
from logic.downloader import DownloadThread
from logic.patcher import PatchExtractor, delete_old_data
from logic.registry import find_steam_game_path
import requests


class GameView(QWidget):
    """Simplified GameView with a single Patch button."""

    def __init__(self):
        super().__init__()
        self.current_game_name = None
        self.is_processing = False
        self.setup_ui()

    def setup_ui(self):
        """Initializes the simplified UI."""
        self.layout = QVBoxLayout(self)

        # Title Label
        self.title_label = QLabel("Siyarbekir's Game-Patcher")
        font = QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Image Label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(505, 300)
        self.layout.addWidget(self.image_label)

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        # Patch Button
        self.patch_button = QPushButton("Patch")
        self.patch_button.setStyleSheet("background-color: green; color: white; font-size: 14pt;")
        self.layout.addWidget(self.patch_button)
        self.patch_button.hide()

        # Connect Patch Button
        self.patch_button.clicked.connect(self.start_patch_process)

    def start_patch_process(self):
        """Handles the entire patching process."""
        if self.is_processing:  # Prevents multiple starts
            return
        self.is_processing = True
        self.patch_button.hide()  # Hides the button

        if not self.current_game_name:
            QMessageBox.warning(self, "Fehler", "Kein Spiel ausgewählt.")
            self.reset_ui()
            return

        # Step 1: Automatically find game path
        app_id = APP_IDS.get(self.current_game_name)
        if not app_id:
            QMessageBox.warning(self, "Fehler", "Keine App-ID für das Spiel gefunden.")
            self.reset_ui()
            return

        game_path = find_steam_game_path(app_id)
        if not game_path:  # Manually select path if not found
            game_path = QFileDialog.getExistingDirectory(self, "Zielverzeichnis auswählen")
            if not game_path:
                QMessageBox.warning(self, "Fehler", "Kein Zielverzeichnis ausgewählt.")
                self.reset_ui()
                return
            else:
                game_path = os.path.normpath(game_path)  # Normalize the path
                logger.info(f"Manually selected path normalized: {game_path}")

        # Step 2: Validate the path
        if not os.path.exists(game_path):
            QMessageBox.critical(self, "Fehler", "Spielpfad konnte nicht gefunden werden.")
            logger.error(f"Game path does not exist: {game_path}")
            self.reset_ui()
            return

        # Step 3: Start download process
        save_path = f"{app_id}.zip"
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.download_thread = DownloadThread(self.current_game_name, save_path)
        self.download_thread.progress.connect(self.progress_bar.setValue)
        self.download_thread.finished.connect(lambda: self.extract_update(save_path, game_path))
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.start()

    def extract_update(self, zip_path, target_path):
        """Extracts the downloaded update with progress tracking."""
        try:
            if not os.path.exists(target_path):
                logger.info(f"Target path does not exist, creating: {target_path}")
                os.makedirs(target_path)

            # Delete old data
            delete_old_data(self.current_game_name,target_path)

            # Validate the ZIP path
            if not os.path.exists(zip_path):
                QMessageBox.critical(self, "Fehler", "Update-Datei nicht gefunden.")
                self.reset_ui()
                return

            self.progress_bar.setValue(0)
            self.progress_bar.setVisible(True)

            # Patch extraction with progress
            self.patch_extractor = PatchExtractor()
            self.patch_extractor.progress.connect(self.progress_bar.setValue)
            self.patch_extractor.extract_patch(zip_path, target_path)

            QMessageBox.information(self, "Erfolg", "Patch erfolgreich angewendet.")
        except Exception as e:
            logger.error(f"Error applying patch: {e}")
            QMessageBox.critical(self, "Fehler beim Patchen", str(e))
        finally:
            self.reset_ui()

    def on_download_error(self, error_message):
        """Handles download errors."""
        QMessageBox.critical(self, "Download fehlgeschlagen", error_message)
        self.progress_bar.setVisible(False)



    def update_view(self, game_name):
        """Updates the view for the selected game."""
        logger.info(f"Updating view for {game_name}.")
        self.current_game_name = game_name
        self.title_label.setText(f"{game_name} - Patcher")
        self.load_game_image(game_name)
        self.patch_button.show()

    def load_game_image(self, game_name):
        """Loads and displays the game image based on the game name."""
        if game_name not in APP_IDS:
            logger.warning(f"No image available for {game_name}.")
            self.image_label.clear()
            self.image_label.setText("Kein Bild verfügbar")
            return

        app_id = APP_IDS[game_name]
        image_url = f"https://siyarbekir.de/downloads/{app_id}.jpeg"

        try:
            logger.info(f"Loading image for {game_name} from {image_url}.")
            response = requests.get(image_url)
            response.raise_for_status()
            image_data = response.content
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            self.image_label.setPixmap(pixmap.scaled(
                self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        except Exception as e:
            logger.error(f"Failed to load image for {game_name}: {e}")
            self.image_label.setText(f"Fehler beim Laden des Bildes: {e}")

    def reset_ui(self):
        """Resets the UI after the patching process."""
        self.progress_bar.setVisible(False)
        self.patch_button.show()
        self.is_processing = False