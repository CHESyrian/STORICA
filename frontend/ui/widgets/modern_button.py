"""
Modern custom button with animations and effects.

Styling lives in theme QSS files (MsgModernButton[type="…"]).
No setStyleSheet in this module.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QPushButton, QStyle
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
)
from PyQt6.QtGui import QFont, QColor, QLinearGradient, QPainter


class ModernButton(QPushButton):
    """Modern button with hover animations and gradient effects."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("ModernButton")
        self._opacity = 1.0
        self.setup_animations()
        self.apply_styles()

    def setup_animations(self):
        """Setup hover animations."""
        self.animation = QPropertyAnimation(self, b"opacity")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def apply_styles(self):
        """Apply modern button styles (geometry only; colors via QSS)."""
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    @pyqtProperty(float)
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.update()

    def enterEvent(self, event):
        """Handle mouse enter event."""
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.85)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self.animation.setStartValue(0.85)
        self.animation.setEndValue(1.0)
        self.animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        """Custom paint for gradient background."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(93, 156, 255))
        gradient.setColorAt(1, QColor(59, 130, 246))

        painter.setOpacity(self._opacity)
        painter.fillRect(self.rect(), gradient)

        painter.setPen(QColor(255, 255, 255))
        painter.drawText(
            self.rect(),
            Qt.AlignmentFlag.AlignCenter,
            self.text(),
        )
        painter.end()


class MsgModernButton(QPushButton):
    """
    Message-dialog button.

    Appearance is driven by the dynamic property ``type``
    (primary / secondary / success / danger) and theme QSS rules
    matching ``MsgModernButton[type="…"]``.
    """

    def __init__(self, text: str, button_type: str = "primary", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setObjectName("MsgModernButton")
        self.setProperty("type", button_type)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(36)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self._repolish()

    def set_button_type(self, button_type: str) -> None:
        """Update type property and refresh QSS."""
        self.button_type = button_type
        self.setProperty("type", button_type)
        self._repolish()

    def _repolish(self) -> None:
        style = self.style()
        if style is not None:
            style.unpolish(self)
            style.polish(self)
        self.update()
