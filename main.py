from PyQt5.QtWidgets import QApplication, QWidget, QSystemTrayIcon, QMenu, QAction, QStyle
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QRectF
from PyQt5.QtGui import QPainter, QColor, QCursor, QFont, QPainterPath

import math
from pynput import keyboard

from fun import *

actions = {
    "OBS": obs,
    "Driver": driver 
}

class KeyboardTrigger(QObject):
    show_signal = pyqtSignal()
    hide_signal = pyqtSignal()

class RadialMenu(QWidget):
    def __init__(self, options = ["1", "2", "3"]):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.is_visible = False
        self.options = options
        self.num_options = len(options)
        self.selected_option = None
        
        self.resize(400, 400)
        self.inner_radius = 50
        self.outer_radius = 180
        
        self.init_tray()
    
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect_full = QRectF(self.rect())
        center = rect_full.center()
        
        cursor_pos = self.mapFromGlobal(QCursor.pos())
        dx = cursor_pos.x() - center.x()
        dy = cursor_pos.y() - center.y()
        distance = math.sqrt(dx** 2 + dy**2)
        
        angle = math.degrees(math.atan2(dx, -dy))
        if angle < 0: angle += 360
        
        sector_width = 360 // self.num_options
        current_sector = int(angle // sector_width)
        
        if distance < self.inner_radius or distance > self.outer_radius:
            self.selected_option = None
        else:
            self.selected_option = self.options[current_sector]
        
        for i in range(self.num_options):
            start_angle = 90 - (i * sector_width)
            is_active = (self.selected_option == self.options[i])
            
            offset_dist = 15 if is_active else 0
            
            pop_angle = math.radians(90 - (i * sector_width + sector_width / 2))
            off_x = offset_dist * math.cos(pop_angle)
            off_y = -offset_dist * math.sin(pop_angle)
            
            rect_basa = rect_full.adjusted(20, 20, -20, -20)
            
            sector_rect = rect_basa.translated(off_x, off_y)
            
            path = QPainterPath()
            path.arcMoveTo(sector_rect, start_angle)
            path.arcTo(sector_rect, start_angle, -sector_width)
            diff = (sector_rect.width() / 2) - self.inner_radius
            rect_inner = sector_rect.adjusted(diff, diff, -diff, -diff)
            path.arcTo(rect_inner, start_angle - sector_width, sector_width)
            path.closeSubpath()
            
            if self.selected_option == self.options[i]:
                painter.setBrush(QColor(0, 120, 215, 220))
            else:
                painter.setBrush(QColor(45, 45, 45, 200)) 
            
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)
            
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            
            t_radius = self.inner_radius + (self.outer_radius - self.inner_radius) / 1.5
            tx = center.x() + off_x + t_radius * math.cos(pop_angle) - 40
            ty = center.y() + off_y - t_radius * math.sin(pop_angle) - 10
            painter.drawText(int(tx), int(ty), 80, 20, Qt.AlignCenter, self.options[i])
        
    def show_at_cursor(self):
        if not self.is_visible:
            pos = QCursor.pos()
            self.move(pos.x() - self.width() // 2, pos.y() - self.height() // 2)
            self.show()
            self.is_visible = True
            self.updata_timer = self.startTimer(16)
    
    def timerEvent(self, e):
        self.update()
    
    def hide_menu(self):
        if self.is_visible:
            if self.selected_option:
                print(f"Виконую: {self.selected_option}")
                
                fun = actions.get(self.selected_option)
                
                if fun:
                    fun()
                else:
                    print("Для цього пункту не призначено функцію")
                    
            self.killTimer(self.updata_timer)
            self.hide()
            self.is_visible = False
            
    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        
        icon = self.style().standardIcon(QStyle.SP_TitleBarMaxButton)
        self.tray_icon.setIcon(icon)
        
        tray_menu = QMenu()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(QApplication.instance().quit)\
        
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.tray_icon.setToolTip("WiProgram")

app = QApplication([])
app.setQuitOnLastWindowClosed(False)
menu = RadialMenu(list(actions.keys()))

trigger = KeyboardTrigger()
trigger.show_signal.connect(menu.show_at_cursor)
trigger.hide_signal.connect(menu.hide_menu)

def on_press(key):
    if key == keyboard.Key.f20:
        trigger.show_signal.emit()
    
def on_release(key):
    if key == keyboard.Key.f20:
        trigger.hide_signal.emit()
        
listener = keyboard.Listener(on_press, on_release)
listener.start()

app.exec()