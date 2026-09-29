from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen
import math


class Spinner(QWidget):
    """Animated circular loading spinner."""

    def __init__(self, parent=None, size=48):
        super().__init__(parent)

        self._angle = 0
        self._line_count = 12

        self.setFixedSize(size, size)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._timer.start(80)

    def _rotate(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()
        radius = min(self.width(), self.height()) // 2 - 4

        for i in range(self._line_count):
            alpha = int(255 * ((i + 1) / self._line_count))

            color = QColor(255, 255, 255)
            color.setAlpha(alpha)

            painter.setPen(
                QPen(
                    color,
                    3,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )

            angle = math.radians(self._angle + i * (360 / self._line_count))

            inner_radius = radius * 0.55

            x1 = center.x() + math.cos(angle) * inner_radius
            y1 = center.y() + math.sin(angle) * inner_radius

            x2 = center.x() + math.cos(angle) * radius
            y2 = center.y() + math.sin(angle) * radius

            painter.drawLine(
                int(x1),
                int(y1),
                int(x2),
                int(y2),
            )