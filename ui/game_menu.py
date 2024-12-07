from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QListWidget
from config import APP_IDS

class GameMenu(QListWidget):
    """
    Eine einfache Spiele-Auswahl-Liste. Wenn auf ein Spiel geklickt wird,
    sendet die Klasse ein Signal mit dem Namen des ausgewählten Spiels.
    """

    # Signal, das ausgelöst wird, wenn ein Spiel ausgewählt wurde
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
        """
        Wird aufgerufen, wenn auf einen Eintrag in der Liste geklickt wird.
        Emitter das `gameSelected`-Signal mit dem Namen des Spiels.
        """
        self.gameSelected.emit(item.text())
