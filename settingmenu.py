from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QTreeWidget, QTreeWidgetItem, QPushButton, QFileDialog
from PyQt5.QtCore import Qt, pyqtSignal

import json
import os

from Ui_SetingMenu import Ui_Form

class SettingMenu(QWidget):

    setting_updated = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        
        self.ui.TreeWidget.setColumnWidth(0, 350)
        self.ui.TreeWidget.setAcceptDrops(True)
        
        self.ui.TreeWidget.customContextMenuRequested.connect(self.open_menu)

        self.ui.Add.clicked.connect(self.add_category)
        self.ui.Confirmed.clicked.connect(self.save)

        self.load()
        
    def load(self):
        self.action = {}
        try:
            with open("action.json", "r", encoding = "utf-8") as a:
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
                child.setFlags(child.flags() | Qt.ItemIsDragEnabled)

    def save(self):
        new_action = {}
        for item in range(self.ui.TreeWidget.topLevelItemCount()):
            parent_item = self.ui.TreeWidget.topLevelItem(item)
            categori_item = parent_item.text(0)
            new_action[categori_item] = []

            for object_ in range(parent_item.childCount()):
                child_item = parent_item.child(object_)
                new_action[categori_item].append({
                    "path": child_item.text(0),
                    "type": child_item.text(1)
                })
        
        self.action = new_action
        print("Save:", new_action)

        try:
            with open("action.json", "w", encoding = "utf-8") as a:
                json.dump(new_action, a,ensure_ascii = False, indent = 4)
        except Exception as e:
            print(e)
        
        self.setting_updated.emit(new_action)
        self.close()
    
    def add_category(self):
        item = QTreeWidgetItem(self.ui.TreeWidget)
        item.setText(0, "New Category")
        item.setFlags(item.flags() | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
        self.ui.TreeWidget.editItem(item, 0)

    def open_menu(self, pos):
        item = self.ui.TreeWidget.itemAt(pos)
        if not item:
            return
        
        menu = QMenu()

        if not item.parent():
            add_file = menu.addAction("📄 Add File")
            add_folde = menu.addAction("📁 Add Foled")
            menu.addSeparator()
            delete = menu.addAction("🗑 Delete")

            action = menu.exec_(self.ui.TreeWidget.viewport().mapToGlobal(pos))
            if action == add_file:
                self.add_file_folder(item, "File")
            if action == add_folde:
                self.add_file_folder(item, "Folder")
            if action == delete:
                self.ui.TreeWidget.takeTopLevelItem(self.ui.TreeWidget.indexOfTopLevelItem(item))
        else:
            delete_path = menu.addAction("🗑 Delete")
            if menu.exec_(self.ui.TreeWidget.viewport().mapToGlobal(pos)) == delete_path:
                item.parent().removeChild(item)
    
    def add_file_folder(self, item, type_):
        if type_ == "File":
            path, _ = QFileDialog.getOpenFileName(self, "Select file")
        else:
            path = QFileDialog.getExistingDirectory(self, "Select foler")
        
        if path:
            child = QTreeWidgetItem(item)
            child.setText(0, path)
            child.setText(1, type_)
            child.setFlags(child.flags() | Qt.ItemIsDragEnabled)
            item.setExpanded(True)
    
if __name__ == "__main__":
    app = QApplication([])
    window = SettingMenu()
    window.show()
    app.exec()