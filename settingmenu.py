import json
import webbrowser

from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QFileDialog, QUndoCommand, QUndoStack, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal, QStandardPaths

from ui.Ui_SettingMenu import Ui_MainWindow
from macrosdialog import MacrosDialog
from functions import active_action
import menu
from classes import dialoggetshortcut, key_handler


desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)


class DelItem(QUndoCommand):
    def __init__(self, tree, item):
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


class SettingMenu(QMainWindow):

    setting_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Menu Setting")

        self.undo_stack = QUndoStack(self)

        self.ui.TreeWidget.setColumnWidth(0, 350)
        self.ui.TreeWidget.setAcceptDrops(True)

        self.setup()
        self.load()

    def setup(self):
        self.ui.TreeWidget.customContextMenuRequested.connect(
            lambda pos: menu.open_menu(self, pos)
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
        self.action = {}

        try:
            with open(path_load, "r", encoding="utf-8") as file:
                self.action = json.load(file)
        except Exception as e:
            print(f"load {e}")

        self.ui.TreeWidget.clear()

        for category, items in self.action.items():
            cat_item = QTreeWidgetItem(self.ui.TreeWidget)
            cat_item.setText(0, category)
            cat_item.setFlags(
                cat_item.flags() | Qt.ItemIsEditable |
                Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
            )
            for item in items:
                child = QTreeWidgetItem(cat_item)
                child.setText(0, item["path"])
                child.setText(1, item["type"])
                if item["type"] == "Macros":
                    content = item['content']
                    content.append(item["path"])
                    child.setData(0, Qt.UserRole, content)
                child.setFlags(
                    child.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled
                )

    def save(self, *, flag=True, path_save="action.json"):
        new_action = {}

        for item in range(self.ui.TreeWidget.topLevelItemCount()):
            parent_item = self.ui.TreeWidget.topLevelItem(item)
            if parent_item.childCount() > 0:
                categori_item = parent_item.text(0)
                new_action[categori_item] = []
                for object_ in range(parent_item.childCount()):
                    child_item = parent_item.child(object_)

                    path = child_item.text(0)
                    type_ = child_item.text(1)

                    if type_ == "Macros":
                        content = child_item.data(0, Qt.UserRole)
                        name = content[-1]
                        content.remove(name)
                        new_action[categori_item].append({
                            "path": name,
                            "content": content,
                            "type": type_
                        })
                        continue
                    new_action[categori_item].append({
                        "path": path,
                        "type": type_
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

    def shortcut(self):
        key = dialoggetshortcut(self)
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

    def add_category(self, *, text=""):
        item = QTreeWidgetItem(self.ui.TreeWidget)
        item.setText(0, text)
        item.setFlags(
            item.flags() | Qt.ItemIsEditable |
            Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        )

        self.ui.TreeWidget.editItem(item, 0)

    def create_action(self, item, path, type_, data=None):
        child = QTreeWidgetItem(item)
        child.setText(0, path)
        if type_ == "Url":
            if not path.startswith(("https://", "http://")):
                path = "https://"+path
        child.setText(1, type_)
        if data:
            child.setData(0, Qt.UserRole, data)
        child.setFlags(
            child.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled
        )
        item.setExpanded(True)

    def add_macros(self):
        dialog = MacrosDialog(self)
        if dialog.exec_():
            return dialog.getMacros()
        return None

    def add_action(self, item, type_):
        match type_:
            case "File":
                path, _ = QFileDialog.getOpenFileName(
                    self, "Select file", desktop_path
                )
            case "Folder":
                path = QFileDialog.getExistingDirectory(
                    self, "Select foler", desktop_path
                )
            case "Url":
                val, ok = QInputDialog.getText(
                    self, "Url", "Entry Url", text="https://example.com"
                )
                if ok:
                    self.create_action(item, val, type_)
                return
            case "Macros":
                macros_list = self.add_macros()
                if macros_list:
                    self.create_action(
                        item, macros_list[-1], type_, macros_list
                    )
                return

        if path:
            self.create_action(item, path, type_)
            return

    def test_action(self, parent: QTreeWidgetItem):
        actions = {}
        actions[parent.text(0)] = []

        for item in range(parent.childCount()):
            child = parent.child(item)
            type_ = child.text(1)
            if type_ == "Macros":
                content = child.data(0, Qt.UserRole)
                name = content[-1]
                content.remove(name)
                actions[parent.text(0)].append({
                    "path": name,
                    "content": content,
                    "type": type_
                })
                continue
            else:
                actions[parent.text(0)].append({
                    "path": child.text(0),
                    "type": type_
                })
        active_action(parent.text(0), actions)

    def del_item(self, item):
        if not item:
            item = self.ui.TreeWidget.currentItem()
        if item:
            self.undo_stack.push(DelItem(self.ui.TreeWidget, item))


def open_setting_window(parent):
    if not hasattr(parent, 'settings_win') or setting_menu is None:
        setting_menu = SettingMenu()

    setting_menu.setting_updated.connect(parent.update_menu)

    setting_menu.show()
    setting_menu.activateWindow()


if __name__ == "__main__":
    app = QApplication([])
    window = SettingMenu()
    window.show()
    app.exec()
