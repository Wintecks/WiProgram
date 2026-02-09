from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject

from pynput import keyboard

from radialmenu import RadialMenu

class KeyboardTrigger(QObject):
    show_signal = pyqtSignal()
    hide_signal = pyqtSignal()

app = QApplication([])
app.setQuitOnLastWindowClosed(False)
menu = RadialMenu()

trigger = KeyboardTrigger()
trigger.show_signal.connect(menu.show_at_cursor)
trigger.hide_signal.connect(menu.hide_menu)

def on_press(key):
    if key == keyboard.Key.f20:
        trigger.show_signal.emit()
    
def on_release(key):
    if key == keyboard.Key.f20:
        trigger.hide_signal.emit()
        
listener = keyboard.Listener(on_press, on_release)
listener.start()

app.exec()