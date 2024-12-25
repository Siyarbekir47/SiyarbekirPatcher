import os
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QMainWindow, QMessageBox, QFileDialog
)

from .main_window_ui import Ui_main_window


from config import APP_IDS, logger
from logic.downloader import DownloadThread
from logic.patcher import PatchExtractor, delete_old_data
from logic.registry import find_steam_game_path


class MainWindow(QMainWindow):


    def __init__(self):
        super().__init__()
        # Designer-UI initialisieren
        self.ui = Ui_main_window()
        self.ui.setupUi(self)
        self.ui.game_menu.addItems(list(APP_IDS.keys()))


        # Statusvariablen
        self.current_game_name = None
        self.is_processing = False

        # Signal-Verbindungen
        self.ui.game_menu.itemClicked.connect(self.on_game_selected)
        self.ui.patch_button.clicked.connect(self.start_patch_process)

        # Fortschrittsbalken am Anfang unsichtbar, Button ausblenden bis etwas gewählt wird
        self.ui.progress_bar.setVisible(False)
        self.ui.patch_button.hide()

        logger.info("MainWindow mit neuer Designer-UI initialisiert.")


    def on_game_selected(self, item):
        """
        Wird aufgerufen, wenn im ListWidget ein Spiel angeklickt wurde.
        """
        game_name = item.text()
        logger.info(f"Game selected: {game_name}")
        self.update_view(game_name)


    def update_view(self, game_name: str):
        """
        Aktualisiert die UI, sobald ein Spiel in der Liste angeklickt wurde.
        """
        logger.info(f"Updating view for {game_name}.")
        self.current_game_name = game_name
        self.ui.title_label.setText(f"{game_name} - Patcher")
        self._load_game_image(game_name)
        self.ui.patch_button.show()

    def _load_game_image(self, game_name: str):
        """
        Lädt das Bild vom Server und zeigt es im UI an.
        """
        if game_name not in APP_IDS:
            logger.warning(f"No image available for {game_name}.")
            self.ui.image_label.clear()
            self.ui.image_label.setText("Kein Bild verfügbar")
            return

        app_id = APP_IDS[game_name]
        image_url = f"https://siyarbekir.de/downloads/{app_id}.jpeg"

        try:
            logger.info(f"Loading image for {game_name} from {image_url}.")
            response = requests.get(image_url)
            response.raise_for_status()

            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.ui.image_label.setPixmap(
                pixmap.scaled(
                    self.ui.image_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
        except Exception as e:
            logger.error(f"Failed to load image for {game_name}: {e}")
            self.ui.image_label.setText(f"Fehler beim Laden des Bildes: {e}")

    def start_patch_process(self):
        """
        Startet den Patch/Download-Prozess, wenn ein Spiel ausgewählt wurde und
        auf den 'Patch'-Button geklickt wird.
        """
        if self.is_processing:
            return
        self.is_processing = True
        self.ui.patch_button.hide()

        if not self.current_game_name:
            QMessageBox.warning(self, "Fehler", "Kein Spiel ausgewählt.")
            self.reset_ui()
            return

        app_id = APP_IDS.get(self.current_game_name)
        if not app_id:
            QMessageBox.warning(self, "Fehler", "Keine App-ID für das Spiel gefunden.")
            self.reset_ui()
            return

        # Spielpfad ermitteln
        game_path = self._get_game_path(app_id)
        if not game_path:
            self.reset_ui()
            return

        if not os.path.exists(game_path):
            QMessageBox.critical(self, "Fehler", "Spielpfad konnte nicht gefunden werden.")
            logger.error(f"Game path does not exist: {game_path}")
            self.reset_ui()
            return

        # Download vorbereiten
        save_path = f"{app_id}.zip"
        self.ui.progress_bar.setValue(0)
        self.ui.progress_bar.setVisible(True)

        # Download-Thread starten
        self.download_thread = DownloadThread(self.current_game_name, save_path)
        self.download_thread.progress.connect(self.ui.progress_bar.setValue)
        self.download_thread.finished.connect(
            lambda: self.extract_update(save_path, game_path)
        )
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.start()

    def _get_game_path(self, app_id: str) -> str:
        """
        Versucht, den Spielpfad automatisch über die Registry zu finden.
        Falls das fehlschlägt, wird der Benutzer nach einem Zielverzeichnis gefragt.
        """
        game_path = find_steam_game_path(app_id)
        if not game_path:
            # Manuelle Auswahl
            game_path = QFileDialog.getExistingDirectory(self, "Zielverzeichnis auswählen")
            if not game_path:
                QMessageBox.warning(self, "Fehler", "Kein Zielverzeichnis ausgewählt.")
                return None
            else:
                game_path = os.path.normpath(game_path)
                logger.info(f"Manually selected path normalized: {game_path}")
        return game_path

    def extract_update(self, zip_path: str, target_path: str):
        """
        Entpackt das heruntergeladene ZIP, löscht alte Daten und aktualisiert das Spielverzeichnis.
        """
        try:
            if not os.path.exists(target_path):
                logger.info(f"Target path does not exist, creating: {target_path}")
                os.makedirs(target_path)

            # Alte Dateien löschen (Config in patcher.py bzw. config.py)
            delete_old_data(self.current_game_name, target_path)

            if not os.path.exists(zip_path):
                QMessageBox.critical(self, "Fehler", "Update-Datei nicht gefunden.")
                self.reset_ui()
                return

            self.ui.progress_bar.setValue(0)
            self.ui.progress_bar.setVisible(True)
            self.patch_extractor = PatchExtractor()
            self.patch_extractor.progress.connect(self.ui.progress_bar.setValue)
            self.patch_extractor.extract_patch(zip_path, target_path)

            QMessageBox.information(self, "Erfolg", "Patch erfolgreich angewendet.")
        except Exception as e:
            logger.error(f"Error applying patch: {e}")
            QMessageBox.critical(self, "Fehler beim Patchen", str(e))
        finally:
            self.reset_ui()

    def on_download_error(self, error_message: str):
        """
        Wird aufgerufen, wenn der Download-Thread einen Fehler gemeldet hat.
        """
        QMessageBox.critical(self, "Download fehlgeschlagen", error_message)
        self.ui.progress_bar.setVisible(False)
        self.reset_ui()

    def reset_ui(self):
        """
        Setzt UI-Elemente nach Patch/Fehler wieder in den Ausgangszustand.
        """
        self.ui.progress_bar.setVisible(False)
        self.ui.patch_button.show()
        self.is_processing = False
