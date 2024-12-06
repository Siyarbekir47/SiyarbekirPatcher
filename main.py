import sys
import os

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def resource_path(relative_path):
    """Gibt den absoluten Pfad zur Ressource zurück, unterstützt PyInstaller."""
    if hasattr(sys, '_MEIPASS'):  # Wenn als .exe ausgeführt, temporärer Ordner von PyInstaller
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)  # Relativer Pfad für Entwicklungsmodus

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Stylesheet laden
    stylesheet_path = resource_path("assets/styles.qss")
    with open(stylesheet_path, "r") as file:
        app.setStyleSheet(file.read())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
