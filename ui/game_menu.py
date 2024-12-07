from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QListWidget
from config import APP_IDS

class GameMenu(QListWidget):
    gameSelected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)
        self.setStyleSheet("background-color: #f0f0f0; font-size: 14px;")

        # Spiele aus APP_IDS laden. APP_IDS ist ein Dict {Spielname: AppID}
        # Wir wollen aber nur die Keys (Spielnamen) anzeigen.
        self.addItems(list(APP_IDS.keys()))

        # Signal verbinden
        self.itemClicked.connect(self.on_item_clicked)

    def on_item_clicked(self, item):
        self.gameSelected.emit(item.text())
