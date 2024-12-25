import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from config import logger, VERSION_URL
from logic.update import check_and_prompt_update
from utils import resource_path
import qdarkstyle


if __name__ == "__main__":
    logger.info("Anwendung wird gestartet...")
    app = QApplication(sys.argv)

    check_and_prompt_update(VERSION_URL)

    window = MainWindow()

    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    window.show()

    sys.exit(app.exec_())
