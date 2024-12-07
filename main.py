import sys
from PyQt5.QtWidgets import QApplication

from logic.update import check_and_prompt_update
from ui.main_window import MainWindow
from config import logger, VERSION_URL
from utils import resource_path

if __name__ == "__main__":
    logger.info("Anwendung wird gestartet...")
    app = QApplication(sys.argv)
    app.setStyle("Fusion")


    stylesheet_path = resource_path("assets/styles.qss")
    try:
        with open(stylesheet_path, "r") as file:
            app.setStyleSheet(file.read())
        logger.info("Stylesheet erfolgreich geladen.")
    except FileNotFoundError:
        logger.warning("Stylesheet (assets/styles.qss) nicht gefunden. Fahre mit Default-Style fort.")
    except Exception as e:
        logger.warning(f"Fehler beim Laden des Stylesheets: {e}. Fahre mit Default-Style fort.")

    check_and_prompt_update(VERSION_URL)


    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
