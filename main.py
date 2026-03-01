import os
import json

from PyQt5.QtWidgets import QApplication

from radialmenu import RadialMenu
from classes import KeyboardTrigger, key_handler


if not os.path.exists("action.json"):
    with open("action.json", "w") as file:
        json.dump({"example": {}}, file, indent=4)

app = QApplication([])
app.setQuitOnLastWindowClosed(False)
menu = RadialMenu()

trigger = KeyboardTrigger()
trigger.show_signal.connect(menu.show_menu)
trigger.hide_signal.connect(menu.hide_menu)

key_handler.start(trigger)
app.exec()
