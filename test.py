import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pynput import mouse, keyboard

# Потік для відстеження подій миші та клавіатури
class RecorderThread(QThread):
    new_event = pyqtSignal(str, str) # Тип дії, Значення

    def __init__(self):
        super().__init__()
        self.running = False

    def run(self):
        self.running = True
        # Створюємо слухачів
        with keyboard.Listener(on_press=self.on_press, on_release=self.on_release) as k_list, \
             mouse.Listener(on_click=self.on_click) as m_list:
            while self.running:
                time.sleep(0.1)
            k_list.stop()
            m_list.stop()

    def on_press(self, key):
        self.new_event.emit("Key Press", str(key))

    def on_release(self, key):
        self.new_event.emit("Key Release", str(key))

    def on_click(self, x, y, button, pressed):
        action = "Mouse Down" if pressed else "Mouse Up"
        self.new_event.emit(action, f"{button} at ({x}, {y})")

    def stop(self):
        self.running = False

class MacroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Macro Recorder")
        self.resize(500, 500)
        
        layout = QVBoxLayout(self)
        
        # Налаштування TreeWidget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Action", "Details"])
        
        # 1. Виділення декількох елементів
        self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # 2. Налаштування Drag and Drop
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDragDropMode(QAbstractItemView.InternalMove)
        
        # Вимикаємо стрілочки зліва (бо в нас немає ієрархії)
        self.tree.setRootIsDecorated(False) 
        
        # Показувати індикатор куди саме ми перетягуємо елемент
        self.tree.setDropIndicatorShown(True)
        
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        layout.addWidget(self.tree)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.record_btn = QPushButton("Start Recording")
        self.record_btn.clicked.connect(self.toggle_recording)
        btn_layout.addWidget(self.record_btn)
        
        # Кнопка ОК для повернення результату
        self.ok_btn = QPushButton("Save Macro")
        self.ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.ok_btn)
        
        layout.addLayout(btn_layout)
        
        self.recorder = RecorderThread()
        self.recorder.new_event.connect(self.add_event_item)

    def add_event_item(self, action, details):
        item = QTreeWidgetItem([action, details])
        
        # --- ЗАБОРОНА ДІТЕЙ ---
        # Вимикаємо прапорець ItemIsDropEnabled для самого елемента.
        # Це означає, що на цей елемент не можна нічого "покласти", 
        # отже він не може стати батьком.
        item.setFlags(item.flags() & ~Qt.ItemIsDropEnabled)
        
        self.tree.addTopLevelItem(item)

    def show_context_menu(self, position):
        menu = QMenu()
        
        # Дії меню
        add_delay = menu.addAction("Add Delay (ms)")
        add_key = menu.addAction("Add Key Manual")
        menu.addSeparator()
        delete_selected = menu.addAction(f"Delete Selected ({len(self.tree.selectedItems())})")
        
        # Відображення
        action = menu.exec_(self.tree.viewport().mapToGlobal(position))
        
        if action == add_delay:
            val, ok = QInputDialog.getInt(self, "Delay", "Enter ms:", 500, 0, 60000, 100)
            if ok: self.add_event_item("Delay", f"{val} ms")
            
        elif action == add_key:
            val, ok = QInputDialog.getText(self, "Key", "Enter key (e.g. 'enter', 'a', 'ctrl'):")
            if ok: self.add_event_item("Manual Key", val)
            
        elif action == delete_selected:
            # --- ВИДАЛЕННЯ ДЕКІЛЬКОХ ЕЛЕМЕНТІВ ---
            selected = self.tree.selectedItems()
            if not selected: return
            
            for item in selected:
                # Видаляємо елемент з дерева
                root = self.tree.invisibleRootItem()
                root.removeChild(item)

    def toggle_recording(self):
        if not self.recorder.isRunning():
            self.recorder.start()
            self.record_btn.setText("STOP (ESC)")
            self.record_btn.setStyleSheet("background-color: red; color: white;")
        else:
            self.recorder.stop()
            self.record_btn.setText("Start Recording")
            self.record_btn.setStyleSheet("")


from PyQt5.QtWidgets import QApplication

app = QApplication([])
w = MacroDialog()
w.show()
app.exec_()