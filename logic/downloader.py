from PyQt5.QtCore import QThread, pyqtSignal
import requests
from config import APP_IDS, logger

class DownloadThread(QThread):
    """
    Ein Thread, um eine Datei (in diesem Fall das Patch-Archiv) herunterzuladen.

    Signale:
        progress(int): Wird emitted, um den aktuellen Fortschritt in % anzuzeigen.
        finished(str): Wird emitted, wenn der Download erfolgreich abgeschlossen ist. Der Parameter ist der Pfad zur gespeicherten Datei.
        error(str): Wird emitted, wenn ein Fehler auftritt. Der Parameter ist die Fehlermeldung.
    """
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, game_name: str, save_path: str):
        """
        Initialisiert den Download-Thread.

        :param game_name: Name des Spiels, das heruntergeladen wird (zur URL-Bestimmung).
        :param save_path: Der lokale Pfad, unter dem die Datei gespeichert werden soll.
        """
        super().__init__()
        self.game_name = game_name
        self.save_path = save_path

    def run(self):
        # Prüfe, ob das Spiel in APP_IDS existiert
        if self.game_name not in APP_IDS:
            error_msg = f"Keine App-ID für das Spiel '{self.game_name}' gefunden."
            logger.error(error_msg)
            self.error.emit(error_msg)
            return

        app_id = APP_IDS[self.game_name]
        zip_url = f"https://siyarbekir.de/downloads/{app_id}.zip"

        logger.info(f"Starte Download für {self.game_name} von {zip_url}")

        try:
            # Stream-Download starten
            response = requests.get(zip_url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            # Datei in Binarystream schreiben
            with open(self.save_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    file.write(chunk)
                    downloaded_size += len(chunk)

                    # Fortschritt berechnen, falls total_size bekannt ist
                    if total_size > 0:
                        progress = int((downloaded_size / total_size) * 100)
                        self.progress.emit(progress)
                    else:
                        # Wenn keine Gesamtgröße vorhanden ist, könnte man 0% oder einen Indikator für "unbekannt" senden.
                        # Hier senden wir einfach 0%.
                        self.progress.emit(0)

            logger.info(f"Download erfolgreich abgeschlossen: {self.save_path}")
            self.finished.emit(self.save_path)

        except requests.HTTPError as http_err:
            # HTTP-Fehler (z. B. 404, 500)
            error_msg = f"HTTP-Fehler beim Download für {self.game_name}: {http_err}"
            logger.error(error_msg)
            self.error.emit(error_msg)

        except requests.RequestException as req_err:
            # Allgemeine Netzwerkfehler, z. B. DNS-Probleme, Timeouts
            error_msg = f"Netzwerkfehler beim Download für {self.game_name}: {req_err}"
            logger.error(error_msg)
            self.error.emit(error_msg)

        except Exception as e:
            # Unerwartete Fehler
            error_msg = f"Unbekannter Fehler beim Download für {self.game_name}: {e}"
            logger.error(error_msg)
            self.error.emit(str(error_msg))
