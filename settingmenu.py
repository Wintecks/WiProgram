import json
import webbrowser
from typing import Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeWidgetItem, QFileDialog,
    QUndoCommand, QUndoStack, QTreeWidget, QWidget, QColorDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QStandardPaths
from PyQt5.QtGui import QColor

from ui.Ui_RadialMenuSetting import Ui_RadialMenuSetting
from macroseditor import MacrosEditor
from functions import active_action
import menu
from classes import GetShortcut, key_handler, InputData
from apieditor import APIEditor


desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)


class DelItem(QUndoCommand):
    def __init__(self, tree: QTreeWidget, item: QTreeWidgetItem):
        super().__init__("Del Item")
        self.tree = tree
        self.item = item
        self.parent = item.parent()
        self.index = -1

    def redo(self):
        if self.parent:
            self.index = self.parent.indexOfChild(self.item)
            self.parent.removeChild(self.item)
        else:
            self.index = self.tree.indexOfTopLevelItem(self.item)
            self.tree.takeTopLevelItem(self.index)

    def undo(self):
        if self.parent:
            self.parent.insertChild(self.index, self.item)
        else:
            self.tree.insertTopLevelItem(self.index, self.item)


class RadialMenuSetting(QMainWindow):

    setting_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.ui = Ui_RadialMenuSetting()
        self.ui.setupUi(self)

        self.undo_stack = QUndoStack(self)
        self.ui.TreeWidget.setColumnWidth(0, 350)

        self.action = {}

        self.setup_connect()
        self.load()

    def setup_connect(self):
        self.ui.TreeWidget.customContextMenuRequested.connect(
            lambda pos: menu.setting_menu(self, pos)
        )

        self.ui.Add.clicked.connect(self.add_category)
        self.ui.Confirmed.clicked.connect(self.save)

        self.ui.actionAdd_category.triggered.connect(self.add_category)
        self.ui.actionShortcut.triggered.connect(self.shortcut)
        self.ui.actionSave.triggered.connect(lambda: self.save(flag=False))
        self.ui.actionImport_Action.triggered.connect(self.import_actions)
        self.ui.actionExport_Action.triggered.connect(self.export_actions)
        self.ui.actionExit.triggered.connect(self.close)

        self.ui.actionUndo.triggered.connect(self.undo_stack.undo)
        self.ui.actionRedo.triggered.connect(self.undo_stack.redo)
        self.ui.actionDelate.triggered.connect(self.del_item)

        self.ui.actionGitHub.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/Wintecks/WiProgram"
            )
        )
        self.ui.actionIssues.triggered.connect(
            lambda: webbrowser.open(
                "https://github.com/Wintecks/WiProgram/issues"
            )
        )

    def load(self, path_load="action.json"):
        try:
            with open(path_load, "r", encoding="utf-8") as file:
                self.action = json.load(file)
        except Exception as e:
            print(f"load error {e}")

        self.ui.TreeWidget.clear()

        for name, data in self.action.items():
            r, g, b, a = data["color"]
            category = self.add_category(
                text=name, color=QColor(r, g, b, a), edit=False
            )

            for child_item in data["actions"]:
                self.create_action(
                    category, child_item["name"], child_item["type"],
                    child_item["data"], False
                )

    def save(self, *, flag=True, path_save="action.json"):
        new_action = {}

        for count in range(self.ui.TreeWidget.topLevelItemCount()):
            top_livel_item = self.ui.TreeWidget.topLevelItem(count)
            if top_livel_item.childCount() > 0:
                categori_item = top_livel_item.text(0)
                new_action[categori_item] = {}
                for object_ in range(top_livel_item.childCount()):
                    child_item = top_livel_item.child(object_)
                    new_action[categori_item].update({
                        "actions": [
                            {
                                "name": child_item.text(0),
                                "type": child_item.text(1),
                                "data": child_item.data(0, Qt.UserRole)
                            }
                        ],
                        "color": top_livel_item.background(0).color().getRgb()
                    })
        self.action = new_action
        try:
            with open(path_save, "w", encoding="utf-8") as file:
                json.dump(new_action, file, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"save {e}")
        if flag:
            self.setting_updated.emit(new_action)
            self.close()

    def add_category(
        self, *, text="", color=QColor(2, 179, 102, 220),
        edit=True
    ):
        category = QTreeWidgetItem(self.ui.TreeWidget)
        category.setText(0, text)
        category.setFlags(
            category.flags() | Qt.ItemIsEditable |
            Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        )
        category.setBackground(0, color)
        if edit:
            self.ui.TreeWidget.editItem(category, 0)

        return category

    def create_action(
        self, item: QTreeWidgetItem, name: str, type_: str, data: Any,
        expanded: bool = True
    ):
        child = QTreeWidgetItem(item, [name, type_])
        child.setData(0, Qt.UserRole, data)
        child.setFlags(
            child.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled |
            ~Qt.ItemIsDropEnabled
        )
        item.setExpanded(expanded)

    def add_action(self, item: QTreeWidgetItem, type_: str, app: str = None):
        match type_:
            case "File":
                InputData(self, type_, item, self.select_file)
            case "Directory":
                InputData(self, type_, item, self.select_directory)
            case "Url":
                InputData(self, type_, item)
            case "Macros":
                dialog = MacrosEditor(parent=self)
                if dialog.exec_():
                    macros = dialog.getMacros()
                    self.create_action(
                        item, macros["name"], type_, macros["macros"]
                    )
            case "App":
                self.create_action(
                    item, app, type_, app
                )
            case "API":
                dialog = APIEditor(parent=self)
                if dialog.exec_():
                    data = dialog.get()
                    self.create_action(
                        item, data.pop("name"), type_, data
                    )

    def select_color(self, item: QTreeWidgetItem):
        r, g, b, a = item.background(0).color().getRgb()
        color = QColorDialog.getColor(
            QColor(r, g, b, a), self, options=QColorDialog.ShowAlphaChannel
        )
        if color:
            item.setBackground(0, color)

    def select_file(self, parent: QWidget):
        path, _ = QFileDialog.getOpenFileName(
            parent, "Select file", desktop_path
        )
        if path:
            return path

    def select_directory(self, parent: QWidget):
        path = QFileDialog.getExistingDirectory(
            parent, "Select directory", desktop_path
        )
        if path:
            return path

    def test_action(self, parent: QTreeWidgetItem):
        actions = {}
        actions[parent.text(0)] = []

        for item in range(parent.childCount()):
            child = parent.child(item)
            actions[parent.text(0)].append({
                "name": child.text(0),
                "type": child.text(1),
                "data": child.data(0, Qt.UserRole)
            })
        active_action(parent.text(0), actions)

    def edit_action(self, item: QTreeWidgetItem):
        data = item.data(0, Qt.UserRole)
        match item.text(1):
            case "File":
                InputData(
                    self, "File", item, self.select_file,
                    name=item.text(0), data=data
                )
            case "Directory":
                InputData(
                    self, "Directory", item, self.select_directory,
                    name=item.text(0), data=data
                )
            case "Url":
                InputData(
                    self, "Url", item,
                    name=item.text(0), data=data
                )
            case "Macros":
                dialog = MacrosEditor(data, item.text(0), self)
                if dialog.exec_():
                    macros = dialog.getMacros()
                    item.setData(0, Qt.UserRole, macros["macros"])
                    item.setText(0, macros["name"])
            case "API":
                dialog = APIEditor(data, item.text(0), self)
                if dialog.exec_():
                    api_data = dialog.get()
                    item.setText(0, api_data.pop("name"))
                    item.setData(0, Qt.UserRole, api_data)

    def del_item(self, item):
        if not item:
            item = self.ui.TreeWidget.currentItem()
        if item:
            self.undo_stack.push(DelItem(self.ui.TreeWidget, item))

    def shortcut(self):
        key = GetShortcut.get_shortcut(self)
        if key:
            key_handler.set_key(key)

    def import_actions(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select file to import actions", desktop_path,
            "Json (*.json);;All File(*.*)"
        )
        if path:
            self.load(path)

    def export_actions(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Select file to export actions",
            f"{desktop_path}/action.json",
            "Json (*.json);;All File(*.*)"
        )

        if path:
            self.save(flag=False, path_save=path)


def open_setting_window(parent):
    setting_menu = RadialMenuSetting()

    setting_menu.setting_updated.connect(parent.update_menu)

    setting_menu.show()
    setting_menu.activateWindow()


if __name__ == "__main__":
    app = QApplication([])
    window = RadialMenuSetting()
    window.show()
    app.exec()
