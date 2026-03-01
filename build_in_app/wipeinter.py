from datetime import datetime
from time import sleep

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QColorDialog, QFileDialog
)
from PyQt5.QtGui import QPainter, QPen, QColor, QMouseEvent, QKeyEvent
from PyQt5.QtCore import Qt, QStandardPaths

if __name__ == "__main__":
    from ui.Ui_Painter import Ui_Painter
else:
    from build_in_app.ui.Ui_Painter import Ui_Painter

desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)


class WiPainter(QMainWindow):
    """Додато що дозволяє малювати по екрану"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Painter()
        self.ui.setupUi(self)

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        self.current_color = QColor(255, 0, 0)
        self.current_width = 5

        self.lines = []
        self.history_stack = []
        self.current_line_points = []

        self.ui.SelectColor.clicked.connect(self.pick_color)
        self.ui.SlideWidth.valueChanged.connect(self.set_width)
        self.ui.Clear.clicked.connect(self.clear)

    def pick_color(self):
        color = QColorDialog.getColor(
            self.current_color, self, "Select color"
        )
        if color:
            self.current_color = color
            self.ui.SelectColor.setStyleSheet(f"""
                background-color: {color.name()};
                border: 2px solid white;
                border-radius: 5px;
            """)

    def set_width(self, val):
        self.current_width = val

    def clear(self):
        self.history_stack.append(list(self.lines))
        self.lines.clear()
        self.update()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))

        for line in self.lines:
            pen = QPen(
                line["color"], line["width"],
                Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin
            )
            painter.setPen(pen)
            points = line["points"]
            if len(points) > 1:
                for item in range(len(points) - 1):
                    painter.drawLine(points[item], points[item+1])

    def mousePressEvent(self, e: QMouseEvent):
        if e.buttons() == Qt.LeftButton:
            self.current_line_points = [e.pos()]
            self.lines.append({
                "points": self.current_line_points,
                "color": QColor(self.current_color),
                "width": self.current_width
            })

    def mouseMoveEvent(self, e: QMouseEvent):
        if e.buttons() & Qt.LeftButton and self.current_line_points:
            self.current_line_points.append(e.pos())
            self.update()

    def getScreenshot(self):
        self.ui.MenuBar.hide()
        QApplication.processEvents()
        screenshot = QApplication.primaryScreen().grabWindow(
            0,
            self.x(),
            self.y(),
            self.width(),
            self.height()
        )
        self.ui.MenuBar.show()
        return screenshot

    def keyPressEvent(self, e: QKeyEvent):
        if e.key() == Qt.Key_Escape:
            self.close()

        elif e.key() == Qt.Key_C and e.modifiers() & Qt.ControlModifier:
            QApplication.clipboard().setPixmap(self.getScreenshot())

        elif e.key() == Qt.Key_S and e.modifiers() & Qt.ControlModifier:
            times = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

            path, _ = QFileDialog.getSaveFileName(
                self, "Select file to export actions",
                f"{desktop_path}/screenshot-{times}.png",
                """
                PNG(*.png);; 
                JPEG(*.jpeg *.jpg *.jpe *.jfif *.jfi *.jif);;All File(*.*)
                """
            )
            if path:
                sleep(0.1)
                self.getScreenshot().save(path)
                self.close()

        elif e.key() == Qt.Key_X and e.modifiers() & Qt.ControlModifier:
            self.clear()

        elif e.key() == Qt.Key_Y and e.modifiers() & Qt.ControlModifier:
            if self.history_stack:
                self.lines.append(self.history_stack.pop())
                self.update()

        elif e.key() == Qt.Key_Z and e.modifiers() & Qt.ControlModifier:
            if not self.lines and self.history_stack:
                last_line = self.history_stack.pop()
                if isinstance(last_line, list):
                    self.lines = last_line
                else:
                    self.lines.append(last_line)
                self.update()
            elif self.lines:
                self.history_stack.append(self.lines.pop())
                self.update()


if __name__ == "__main__":
    app = QApplication([])
    window = WiPainter()
    window.show()
    app.exec_()
