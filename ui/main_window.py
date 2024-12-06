
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget
from ui.game_menu import GameMenu
from ui.game_view import GameView
from config import logger

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Siyarbekir's Game-Patcher")
        self.setMinimumSize(600, 500)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.menu = GameMenu()
        self.view = GameView()
        self.main_layout.addWidget(self.menu)
        self.main_layout.addWidget(self.view)
        self.menu.selection_changed.connect(self.view.update_view)
        logger.info("MainWindow initialized.")
