import re
import json

from PyQt5 import QtWidgets, QtCore, QtGui
from pynput import keyboard


SETTING = QtCore.QSettings("WI", "Program")


class Ui_APIResponseView(object):
    def setupUi(self, APIResponseView):
        APIResponseView.setObjectName("APIResponseView")
        self.horizontalLayout = QtWidgets.QHBoxLayout(APIResponseView)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.TextEdit = QtWidgets.QPlainTextEdit(APIResponseView)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(9)
        self.TextEdit.setFont(font)
        self.TextEdit.viewport().setProperty(
            "cursor", QtGui.QCursor(QtCore.Qt.IBeamCursor)
        )
        self.TextEdit.setTabChangesFocus(False)
        self.TextEdit.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.TextEdit.setObjectName("TextEdit")
        self.horizontalLayout.addWidget(self.TextEdit)

        self.retranslateUi(APIResponseView)
        QtCore.QMetaObject.connectSlotsByName(APIResponseView)

    def retranslateUi(self, APIResponseView):
        _translate = QtCore.QCoreApplication.translate
        APIResponseView.setWindowTitle(
            _translate("APIResponseView", "Dialog")
        )


class JsonHighlighter(QtGui.QSyntaxHighlighter):
    def highlightBlock(self, text):
        fmt = QtGui.QTextCharFormat()
        fmt.setForeground(QtGui.QColor("#1069c2"))
        for match in re.finditer(r'"[^"\\]*"(?=\s*:)|[{}[]]', text):
            self.setFormat(match.start(), match.end() - match.start(), fmt)


class APIResponseView(QtWidgets.QDialog):
    def __init__(self, data, title="", parent=None):
        super().__init__(parent)
        self.ui = Ui_APIResponseView()
        self.ui.setupUi(self)
        self.setWindowTitle(title)
        self.doc = self.ui.TextEdit.document()
        self.highlighter = JsonHighlighter(self.doc)

        self.ui.TextEdit.setPlainText(
            json.dumps(data, indent=4, ensure_ascii=False)
        )
        self.adjust_size()

    def adjust_size(self):
        height = min(self.doc.blockCount() * 20 + 40, 600)
        self.resize(
            320, height
        )


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
