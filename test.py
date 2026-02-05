import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QPushButton, 
                             QStyle, QLabel, QScrollArea, QVBoxLayout)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class IconViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QStyle Icons Viewer")
        self.resize(900, 700)
        
        # Головний лейаут
        main_layout = QVBoxLayout(self)
        
        # Створюємо область прокрутки
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        # Контейнер для іконок
        container = QWidget()
        grid = QGridLayout(container)
        scroll.setWidget(container)

        # Отримуємо всі назви стандартних піктограм (StandardPixmap)
        icons = [i for i in dir(QStyle) if i.startswith('SP_')]
        
        for n, icon_name in enumerate(icons):
            try:
                # Отримуємо саму константу (наприклад, QStyle.SP_DirIcon)
                icon_const = getattr(QStyle, icon_name)
                # Отримуємо іконку від поточної системи
                icon = self.style().standardIcon(icon_const)
                
                # Кнопка з іконкою
                btn = QPushButton()
                btn.setIcon(icon)
                btn.setFixedSize(40, 40)
                
                # Текстова назва
                label = QLabel(icon_name)
                label.setTextInteractionFlags(Qt.TextSelectableByMouse) # Можна копіювати текст
                
                grid.addWidget(btn, n, 0)
                grid.addWidget(label, n, 1)
            except Exception as e:
                print(f"Помилка для {icon_name}: {e}")
                continue

if __name__ == "__main__":
    app = QApplication(sys.argv)
    view = IconViewer()
    view.show()
    sys.exit(app.exec_())