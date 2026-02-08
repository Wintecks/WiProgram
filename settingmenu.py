from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QTreeWidgetItem, QFileDialog, QUndoCommand, QUndoStack, QTreeWidget
from PyQt5.QtCore import Qt, pyqtSignal, QStandardPaths

import json
import webbrowser

from ui.Ui_SetingMenu import Ui_MainWindow

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

        self.clipboard = None
        self.undo_stack = QUndoStack(self)
        
        self.ui.TreeWidget.setColumnWidth(0, 350)
        self.ui.TreeWidget.setAcceptDrops(True)

        self.setup()
        self.load()
    
    def setup(self):
        self.ui.TreeWidget.customContextMenuRequested.connect(self.open_menu)

        self.ui.Add.clicked.connect(self.add_category)
        self.ui.Confirmed.clicked.connect(self.save)


        self.ui.actionAdd_category.triggered.connect(self.add_category)
        # ----------------------------------
        self.ui.actionSave.triggered.connect(lambda: self.save(flag = False))
        # ----------------------------------
        self.ui.actionImport_Action.triggered.connect(self.import_actions)
        self.ui.actionExport_Action.triggered.connect(self.export_actions)
        # ----------------------------------
        self.ui.actionExit.triggered.connect(self.close)

        # ##################################

        self.ui.actionUndo.triggered.connect(self.undo_stack.undo)
        self.ui.actionRedo.triggered.connect(self.undo_stack.redo)
        # ----------------------------------
        self.ui.actionDelate.triggered.connect(self.del_item)
    
        # ##################################
        
        self.ui.actionGitHub.triggered.connect(lambda: webbrowser.open("https://github.com/Wintecks/WiProgram"))
    
    # =====================================================================================
        
    def load(self, path_load = "action.json"):
        self.action = {}
        try:
            with open(path_load, "r", encoding = "utf-8") as a:
                self.action = json.load(a)
        except Exception as e:
            print(e)
        self.ui.TreeWidget.clear()
        
        for category, items in self.action.items():
            cat_item = QTreeWidgetItem(self.ui.TreeWidget)
            cat_item.setText(0, category)
            cat_item.setFlags(cat_item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
            
            for item in items:
                child = QTreeWidgetItem(cat_item)
                child.setText(0, item["path"])
                child.setText(1, item["type"])
                child.setFlags(child.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled)

    def save(self, *, flag = True, path_save = "action.json"):
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

                    if type_ == "Url":
                        if "https://" | "http://" not in path:
                            path = "https://"+path
                    
                    new_action[categori_item].append({
                        "path": path,
                        "type": type_
                    })
        
        self.action = new_action
        try:
            with open(path_save, "w", encoding = "utf-8") as a:
                json.dump(new_action, a, ensure_ascii = False, indent = 4)
        except Exception as e:
            print(e)
        
        if flag:
            print("Save:", new_action)
            self.setting_updated.emit(new_action)
            self.close()
    
    def import_actions(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select file to import actions", desktop_path,
            "Json (*.json);;All File(*.*)"
            )
        if path:
            self.load(path)

    def export_actions(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Select file to export actions", f"{desktop_path}/action.json",
            "Json (*.json);;All File(*.*)"
            )

        if path:
            self.save(flag = False, path_save = path)
    
    # =====================================================================================

    def add_category(self, text = ""):
        item = QTreeWidgetItem(self.ui.TreeWidget)
        item.setText(0, text)
        item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        self.ui.TreeWidget.editItem(item, 0)

    def create_action(self, item, type_, content):
        child = QTreeWidgetItem(item)
        child.setText(0, content)
        child.setText(1, type_)
        child.setFlags(child.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled)
        item.setExpanded(True)
                
    def add_action(self, item, type_):
        match type_:
            case "File":
                path, _ = QFileDialog.getOpenFileName(self, "Select file")
            case "Folder":
                path = QFileDialog.getExistingDirectory(self, "Select foler")
            case "Url":
                self.create_action(item, type_, "https://example.com")
                return
        
        if path:
            self.create_action(item, type_, path)
            return
    
    def del_item(self, item):
        if not item:
            item = self.ui.TreeWidget.currentItem()

        if item:
            self.undo_stack.push(DelItem(self.ui.TreeWidget, item))

    # =====================================================================================

    def open_menu(self, pos):
        item = self.ui.TreeWidget.itemAt(pos)
        if not item:
            return
        
        menu = QMenu()

        if not item.parent():

            add_file = QAction("Add File", self)
            add_file.triggered.connect(lambda: self.add_action(item, "File"))
            add_folde = QAction("Add Foled", self)
            add_folde.triggered.connect(lambda: self.add_action(item, "Folder"))
            add_url = QAction("Add Url", self)
            add_url.triggered.connect(lambda: self.add_action(item, "Url"))
            delete = QAction("Delete", self)
            delete.triggered.connect(lambda: self.del_item(item))
            
            menu.addActions([add_file, add_folde, add_url])
            menu.addSeparator()
            menu.addAction(delete)
        else:
            delete_path = QAction("🗑 Delete", self)
            delete_path.triggered.connect(lambda: self.del_item(item))
            menu.addAction(delete_path)
        
        menu.exec_(self.ui.TreeWidget.viewport().mapToGlobal(pos))

if __name__ == "__main__":
    app = QApplication([])
    window = SettingMenu()
    window.show()
    app.exec()