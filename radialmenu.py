import math
import json
import os

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QColor, QCursor, QFont, QPainterPath

from functions import active_action
from menu import tray


class RadialMenu(QWidget):
    """Радільне меню"""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        try:
            with open("action.json", "r", encoding="utf-8") as file:
                actions = json.load(file)
        except json.decoder.JSONDecodeError:
            with open("action.json", "w") as file:
                json.dump({"example": {}}, file, indent=4)
                actions = {"example": {}}

        options = list(actions.keys())

        self.is_visible = False
        self.actions_ = actions
        self.options = options
        self.num_options = len(options)
        self.selected_option = None

        self.resize(500, 500)
        self.inner_radius = 50
        self.outer_radius = 230

        tray(self)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect_full = QRectF(self.rect())
        center = rect_full.center()

        cursor_pos = self.mapFromGlobal(QCursor.pos())
        dx = cursor_pos.x() - center.x()
        dy = cursor_pos.y() - center.y()
        distance = math.sqrt(dx**2 + dy**2)

        angle = math.degrees(math.atan2(dx, -dy))
        if angle < 0:
            angle += 360

        sector_width = 360.0 / self.num_options
        current_sector = int(angle // sector_width) % self.num_options

        if distance < self.inner_radius or distance > self.outer_radius + 20:
            self.selected_option = None
        else:
            self.selected_option = self.options[current_sector]

        for i in range(self.num_options):
            start_angle = 90 - (i * sector_width)
            is_active = (self.selected_option == self.options[i])

            offset_dist = 15 if is_active else 0

            pop_angle = math.radians(
                90 - (i * sector_width + sector_width / 2)
            )
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
                painter.setBrush(QColor(2, 179, 102, 220))
            else:
                painter.setBrush(QColor(45, 45, 45, 200))

            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))

            t_radius = self.inner_radius + (
                self.outer_radius - self.inner_radius
            ) / 1.5
            tx = center.x() + off_x + t_radius * math.cos(pop_angle) - 40
            ty = center.y() + off_y - t_radius * math.sin(pop_angle) - 10
            painter.drawText(
                int(tx), int(ty), 80, 20, Qt.AlignCenter, self.options[i]
            )

    def timerEvent(self, e):
        self.update()

    def update_menu(self, data: dict):
        self.actions_ = data
        options = list(data.keys())
        self.options = options
        self.num_options = len(options)
        self.update()

    def show_menu(self):
        if not self.is_visible:
            pos = QCursor.pos()
            self.move(
                pos.x() - self.width() // 2, pos.y() - self.height() // 2
            )
            self.show()
            self.is_visible = True
            self.updata_timer = self.startTimer(16)

    def hide_menu(self):
        if self.is_visible:
            self.killTimer(self.updata_timer)
            self.hide()
            self.is_visible = False

            if self.selected_option:
                active_action(self.selected_option, self.actions_)
