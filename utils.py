import sys
import os


def resource_path(relative_path: str) -> str:
    """
    Gibt den absoluten Pfad zur Ressource zurück, unabhängig davon,
    ob das Programm als .exe (PyInstaller) oder als Skript läuft.

    :param relative_path: Der relative Pfad zur Ressource (z. B. "assets/styles.qss")
    :return: Absoluter Pfad zur Ressource
    """
    if hasattr(sys, '_MEIPASS'):  # Falls als .exe durch PyInstaller ausgeführt
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)  # Entwicklungsmodus
