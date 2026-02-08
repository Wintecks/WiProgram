from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QAction, QTreeWidgetItem, QFileDialog, QUndoCommand, QUndoStack, QDialog, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal, QStandardPaths, QThread

import time
import json
import webbrowser
from pynput import mouse, keyboard

from ui.Ui_SettingMenu import Ui_MainWindow
from ui.dialog.Ui_Macros import Ui_Dialog

desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)

class RecorderMacros(QThread):
    new_event = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.running = False
    
    def run(self):
        self.running = True

        with keyboard.Listener(on_press = self.on_press, on_release = self.on_release) as \
            key_list, mouse.Listener(on_click = self.on_click) as mouse_list:
            while self.running:
                time.sleep(0.1)
            key_list.stop()
            key_list.stop()
     
    def on_press(self, key):
        self.new_event.emit("Key Press", str(key))
    
    def on_release(self, key):
        self.new_event.emit("Key Release", str(key))
    
    def on_click(self, x, y, button, preesed):
        action = "Mouse Down" if preesed else "Mouse Up"
        self.new_event.emit(action, f"{button}, {x}, {y}")

    def stop(self):
        self.running = False

class MacrosDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.recorder = RecorderMacros()
        self.recorder.new_event.connect(self.add_item)

        self.ui.TreeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.TreeWidget.customContextMenuRequested.connect(self.show_context_menu)

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
    
    def save_macros(self):
        val, ok = QInputDialog.getText(self, "Name macros", "Entry name:")
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
    
    def add_delay(self):
        val, ok = QInputDialog.getInt(self, "Deley", "Entry ms:", 500, 0, 60000, 100)
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

    def toggle_recording(self):
        if not self.recorder.isRunning():
            self.recorder.start()
            self.ui.StartRecord.setText("Stop (ESC)")
            self.ui.StartRecord.setStyleSheet("background-color: red")
        else:
            self.recorder.stop()
            self.ui.StartRecord.setText("Start Record")
            self.ui.StartRecord.setStyleSheet("")
    
    def add_item(self, action, details):
        item = QTreeWidgetItem([action, details])

        item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled)

        self.ui.TreeWidget.addTopLevelItem(item)
    
    def getMacros(self) -> list:
        return self.macros_list

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
            print(f"load {e}")
        
        self.ui.TreeWidget.clear()
        
        for category, items in self.action.items():
            cat_item = QTreeWidgetItem(self.ui.TreeWidget)
            cat_item.setText(0, category)
            cat_item.setFlags(cat_item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
            
            for item in items:
                child = QTreeWidgetItem(cat_item)
                child.setText(0, item["path"])
                child.setText(1, item["type"])
                if item["type"] == "Macros":
                    content = item['content']
                    content.append(item["path"])
                    child.setData(0, Qt.UserRole, content)
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
                    elif type_ == "Macros":
                        content = child_item.data(0, Qt.UserRole)
                        name = content[-1]
                        content.remove(name)
                        new_action[categori_item].append({
                            "path": name,
                            "content" : content,
                            "type": type_
                        })
                        continue
                    
                    new_action[categori_item].append({
                        "path": path,
                        "type": type_
                    })
        
        self.action = new_action
        try:
            with open(path_save, "w", encoding = "utf-8") as a:
                json.dump(new_action, a, ensure_ascii = False, indent = 4)
        except Exception as e:
            print(f"save {e}")
        
        if flag:
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

    def add_category(self, *, text = ""):
        item = QTreeWidgetItem(self.ui.TreeWidget)
        item.setText(0, text)
        item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        self.ui.TreeWidget.editItem(item, 0)

    def create_action(self, item, path, type_, data = None):
        child = QTreeWidgetItem(item)
        child.setText(0, path)
        child.setText(1, type_)
        if data:
            child.setData(0, Qt.UserRole, data)
        child.setFlags(child.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled)
        item.setExpanded(True)

    def add_macros(self):
        dialog = MacrosDialog(self)
        if dialog.exec_():
            return dialog.getMacros()
        return None
                
    def add_action(self, item, type_):
        match type_:
            case "File":
                path, _ = QFileDialog.getOpenFileName(self, "Select file")
            case "Folder":
                path = QFileDialog.getExistingDirectory(self, "Select foler")
            case "Url":
                self.create_action(item, "https://example.com", type_)
                return
            case "Macros":
                macros_list = self.add_macros()
                if macros_list:
                    self.create_action(item, macros_list[-1], type_, macros_list)
                return
        
        if path:
            self.create_action(item, path, type_)
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
            add_macros = QAction("Add Macros", self)
            add_macros.triggered.connect(lambda: self.add_action(item, "Macros"))
            delete = QAction("Delete", self)
            delete.triggered.connect(lambda: self.del_item(item))
            
            menu.addActions([add_file, add_folde, add_url, add_macros])
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