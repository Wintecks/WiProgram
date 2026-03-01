from PyQt5.QtWidgets import (
    QMenu, QAction, QTreeWidgetItem, QDialog, QInputDialog, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from pynput import mouse, keyboard

from ui.dialog.Ui_Macros import Ui_Dialog


class RecorderMacros(QThread):
    """Зписувач натиснутих клавіш"""

    new_event = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()

    def on_press(self, key):
        self.new_event.emit("Key Press", str(key))

    def on_release(self, key):
        self.new_event.emit("Key Release", str(key))

    def on_click(self, x, y, button, preesed):
        action = "Mouse Down" if preesed else "Mouse Up"
        self.new_event.emit(action, f"{button}, {x}, {y}")

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


class MacrosDialog(QDialog):
    """Вікно створеня макросів"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.recorder = RecorderMacros()
        self.recorder.new_event.connect(self.add_item)
        self.is_recorder = False
        self.save_text = ""

        self.ui.TreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.TreeWidget.customContextMenuRequested.connect(
            self.show_context_menu
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
            self.macros_list = []
            for object_ in range(self.ui.TreeWidget.topLevelItemCount()):
                item = self.ui.TreeWidget.topLevelItem(object_)
                self.macros_list.append({
                    "action": item.text(0),
                    "datals": item.text(1)
                })
            self.macros_list.append(val)
            self.accept()

    def add_item(self, action, details):
        item = QTreeWidgetItem([action, details])

        item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled)

        self.ui.TreeWidget.addTopLevelItem(item)

    def add_delay(self):
        val, ok = QInputDialog.getInt(
            self, "Deley", "Entry ms:", 500, 0, 60000, 100)
        if ok:
            self.add_item("Delay", val)

    def add_key(self):
        val, ok = QInputDialog.getText(self, "Key", "Entry key:")
        if ok:
            self.add_item("Key Press", f"{val}")
            self.add_item("Key Release", f"{val}")

    def del_item(self):
        select = self.ui.TreeWidget.selectedItems()
        if not select:
            return

        for item in select:
            self.ui.TreeWidget.invisibleRootItem().removeChild(item)

    def show_context_menu(self, pos):
        menu = QMenu()

        add_delay = QAction("Add Dalay (ms)", self)
        add_delay.triggered.connect(self.add_delay)
        add_key = QAction("Add Key", self)
        add_key.triggered.connect(self.add_key)

        menu.addActions([add_delay, add_key])
        menu.addSeparator()
        menu.addAction(self.del_item_action)

        menu.exec_(self.ui.TreeWidget.viewport().mapToGlobal(pos))

    def setMacros(self, content: list, name):
        self.save_text = name
        for item in content:
            self.add_item(item["action"], item["datals"])

    def getMacros(self) -> list:
        """Отримати список макроса"""
        return self.macros_list


if __name__ == "__main__":
    app = QApplication([])
    window = MacrosDialog()
    window.show()
    app.exec()
