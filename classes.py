import re
import json
from typing import Callable

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from pynput import keyboard

from ui.dialog.Ui_InputData import Ui_InputData


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
            "cursor", QtGui.QCursor(Qt.IBeamCursor)
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
    def __init__(self, data, title="", parent: QtWidgets.QWidget = None):
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


class InputData(QtWidgets.QDialog):
    def __init__(
        self, parent: QtWidgets.QWidget = None, type_="",
        item: QtWidgets.QTreeWidgetItem = None, fun: Callable[[]] = None,
        name: str = None, data: str = None,
    ):
        super().__init__(parent)
        self.ui = Ui_InputData()
        self.ui.setupUi(self)

        self.setWindowTitle(name)

        self.ui.LineName.setText(name)
        self.ui.LineData.setText(data)
        self.ui.LineData.textChanged.connect(self.auto_name)
        self.ui.CheckBox.stateChanged.connect(self.auto_name)
        self.ui.ToolButton.clicked.connect(self.insert_data)

        self.fun = fun
        self.item = item
        self.type_ = type_
        self.name = name
        self.data = data

        self.ui.LineData.setPlaceholderText(type_)

        if not fun:
            self.ui.ToolButton.setEnabled(False)

        self.exec_()

    def insert_data(self):
        self.ui.LineData.setText(self.fun(self))

    def auto_name(self):
        if self.ui.CheckBox.isChecked():
            self.ui.LineName.setText(self.ui.LineData.text())

    def accept(self):
        name = self.ui.LineName.text()
        if not self.name:
            child = QtWidgets.QTreeWidgetItem(self.item, [name, self.type_])
            child.setData(0, Qt.UserRole, self.ui.LineData.text())
            child.setFlags(
                child.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled |
                ~Qt.ItemIsDropEnabled
            )
            self.item.setExpanded(True)
        else:
            self.item.setText(0, name)
            self.item.setData(0, Qt.UserRole, self.ui.LineData.text())
        return super().accept()


class GetShortcut(QtWidgets.QDialog):
    """Діалого вікно для отриманя клавіші"""

    def __init__(self, parent: QtWidgets.QWidget = None):
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

    @staticmethod
    def get_shortcut(parent: QtWidgets.QWidget = None) -> str:
        dialog = GetShortcut(parent)
        if dialog.exec_():
            return dialog.key_edit.keySequence().toString()
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
