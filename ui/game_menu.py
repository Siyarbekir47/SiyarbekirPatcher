from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QListWidget


class GameMenu(QListWidget):
    # Signal, das beim Klicken auf ein Spiel ausgelöst wird
    selection_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")
        self.addItems(["Lethal Company", "Elden Ring"])

        # Signal verbinden
        self.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item):
        self.selection_changed.emit(item.text())
