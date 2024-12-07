from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget
from ui.game_menu import GameMenu
from ui.game_view import GameView
from config import logger


class MainWindow(QMainWindow):
    """
    Das Hauptfenster der Anwendung. Es beinhaltet ein seitliches Menü (GameMenu)
    zur Auswahl von Spielen und eine Ansicht (GameView), in der je nach Auswahl
    Inhalte angezeigt und Patch-Vorgänge angestoßen werden.
    """

    def __init__(self):
        """
        Initialisiert das Hauptfenster, setzt Titel, Mindestgröße und
        erstellt die Hauptlayout-Elemente.
        """
        super().__init__()
        self.setWindowTitle("Siyarbekir's Game-Patcher")
        self.setMinimumSize(600, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.menu = GameMenu()
        self.view = GameView()

        self.setup_ui()
        self.connect_signals()

        logger.info("MainWindow initialized.")

    def setup_ui(self):
        """Richtet das Hauptlayout ein und fügt Menü- und View-Komponente hinzu."""
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.menu)
        self.main_layout.addWidget(self.view)

    def connect_signals(self):
        """
        Verbindet Signale des GameMenu mit Slots der GameView.
        Wenn ein Spiel im Menü ausgewählt wird, wird die View entsprechend aktualisiert.
        """
        self.menu.gameSelected.connect(self.view.update_view)
