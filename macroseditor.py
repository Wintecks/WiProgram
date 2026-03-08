from PyQt5.QtWidgets import (
    QAction, QTreeWidgetItem, QDialog, QInputDialog, QApplication, QMainWindow
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from pynput import mouse, keyboard

from ui.dialog.Ui_MacrosEditor import Ui_MacrosEditor
import menu
from classes import GetShortcut


class RecorderMacros(QThread):
    """Зписувач натиснутих клавіш"""

    new_event = pyqtSignal(list)

    def __init__(self):
        super().__init__()

    def on_press(self, key):
        self.new_event.emit(["Key Press", str(key)])

    def on_release(self, key):
        self.new_event.emit(["Key Release", str(key)])

    def on_click(self, x, y, button, preesed):
        action = "Mouse Down" if preesed else "Mouse Up"
        self.new_event.emit([action, f"{button}, {x}, {y}"])

    def start(self):
        self.key_listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.mause_listener = mouse.Listener(on_click=self.on_click)
        self.key_listener.start()
        self.mause_listener.start()

    def stop(self):
        self.key_listener.stop()
        self.mause_listener.stop()
        self.quit()


class MacrosEditor(QDialog):
    """Вікно створеня макросів"""

    def __init__(
        self, data: list = None, name: str = "", parent: QMainWindow = None
    ):
        super().__init__(parent)
        self.ui = Ui_MacrosEditor()
        self.ui.setupUi(self)

        self.recorder = RecorderMacros()
        self.recorder.new_event.connect(self.add_item)
        self.is_recorder = False
        self.save_text = name
        self.macros = {}

        if data:
            for data_item in data:
                self.add_item([data_item["action"], data_item["data"]])

        self.ui.TreeWidget.customContextMenuRequested.connect(
            lambda pos: menu.macros_menu(self, pos)
        )

        self.ui.StartRecord.clicked.connect(self.toggle_recording)
        self.ui.SelectAll.clicked.connect(self.ui.TreeWidget.selectAll)
        self.ui.SaveMacros.clicked.connect(self.save_macros)
        self.ui.Clear.clicked.connect(self.ui.TreeWidget.clear)

        self.del_item_action = QAction("Delete", self)
        self.del_item_action.setShortcut("Del")
        self.del_item_action.triggered.connect(self.del_item)
        self.addAction(self.del_item_action)

        save = QAction("Save", self)
        save.setShortcut("Ctrl+S")
        save.triggered.connect(self.save_macros)
        self.addAction(save)

    def toggle_recording(self):
        if not self.is_recorder:
            self.recorder.start()
            self.ui.StartRecord.setText("Stop (ESC)")
            self.ui.StartRecord.setStyleSheet("background-color: red")
            self.is_recorder = True
        else:
            self.recorder.stop()
            self.ui.StartRecord.setText("Start Record")
            self.ui.StartRecord.setStyleSheet("")
            self.is_recorder = False

    def save_macros(self):
        val, ok = QInputDialog.getText(
            self, "Name macros", "Entry name:",
            text=self.save_text
        )
        if ok:
            macros_list = []
            for object_ in range(self.ui.TreeWidget.topLevelItemCount()):
                item = self.ui.TreeWidget.topLevelItem(object_)
                macros_list.append({
                    "action": item.text(0),
                    "data": item.text(1)
                })
            self.macros["macros"] = macros_list
            self.macros["name"] = val
            self.accept()

    def add_item(self, data: list):
        item = QTreeWidgetItem(self.ui.TreeWidget, data)
        item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled)
        self.ui.TreeWidget.addTopLevelItem(item)

    def del_item(self):
        select = self.ui.TreeWidget.selectedItems()
        if not select:
            return

        for item in select:
            self.ui.TreeWidget.invisibleRootItem().removeChild(item)

    def add_delay(self):
        val, ok = QInputDialog.getInt(
            self, "Deley", "Entry ms:", 500, 0, 60000, 100
        )
        if ok:
            self.add_item(["Delay", str(val)])

    def add_key(self):
        key = GetShortcut.get_shortcut(self)
        if key:
            self.add_item(["Key Press", f"{key}"])
            self.add_item(["Key Release", f"{key}"])

    def getMacros(self) -> list:
        """Отримати список макроса"""
        return self.macros


if __name__ == "__main__":
    app = QApplication([])
    window = MacrosEditor()
    window.show()
    app.exec()
    # print(window.getMacros())
