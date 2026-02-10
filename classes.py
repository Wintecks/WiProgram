from PyQt5 import QtWidgets, QtCore
from pynput import keyboard


SETTING = QtCore.QSettings("WI", "Program")


class ShortcutDialog(QtWidgets.QDialog):
    """Діалого вікно для отриманя клавіші"""

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Shortcut")

        label = QtWidgets.QLabel("Press key:")
        self.key_edit = QtWidgets.QKeySequenceEdit(self)
        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok |
            QtWidgets.QDialogButtonBox.Cancel, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.key_edit)
        layout.addWidget(buttons)

    def get_shortcut(self) -> str:
        """Отримати обрану клавішу"""
        return self.key_edit.keySequence().toString()


def dialoggetshortcut(parent=None) -> str:
    """Створити вікно та отримати клавішу або нічого"""
    dialog = ShortcutDialog(parent)
    if dialog.exec_():
        return dialog.get_shortcut()
    return None


class KeyboardTrigger(QtCore.QObject):
    show_signal = QtCore.pyqtSignal()
    hide_signal = QtCore.pyqtSignal()


class KeyListener:
    def __init__(self):
        key = SETTING.value("KeyOpenRadialMenu")
        if not key:
            self.set_key('`')
        else:
            self.key = key

        self.listener = keyboard.Listener(
            self.on_press, self.on_release
        )

    def set_key(self, key_str: str):

        key_str = key_str.strip().strip("'").lower()

        try:
            if hasattr(keyboard.Key, key_str.lower()):
                self.key = getattr(keyboard.Key, key_str.lower())
            else:
                self.key = keyboard.KeyCode.from_char(key_str)
            SETTING.setValue("KeyOpenRadialMenu", self.key)
            print(
                f"Клавішу успішно змінено на: {key_str}")
        except Exception as e:
            print(
                f"Помилка встоновлкення клавіші: {e}")
            SETTING.setValue("KeyOpenRadialMenu", None)

    def on_press(self, key):
        if key == self.key:
            self.trigger.show_signal.emit()

    def on_release(self, key):
        if key == self.key:
            self.trigger.hide_signal.emit()

    def start(self, trigger):
        self.trigger = trigger
        self.listener.start()


key_handler = KeyListener()
