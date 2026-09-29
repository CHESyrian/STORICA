"""
Toast notification widget.

Styling lives in theme QSS files via object names and the dynamic
property ``toastType`` (info / success / warning / error).
No setStyleSheet in this module.
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QFrame,
    QGraphicsOpacityEffect,
    QStyle,
)
from PyQt6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    pyqtProperty,
    QRectF,
)
from PyQt6.QtGui import QFont, QPainter, QColor, QPainterPath, QBrush


class Toast(QFrame):
    """Custom toast notification widget with professional styling."""

    ANIMATION_DURATION = 300
    DISPLAY_DURATION = 3000

    _ICON = {
        "success": "✓",
        "error": "✗",
        "warning": "⚠",
        "info": "ℹ",
    }

    def __init__(
        self,
        message: str,
        parent: Optional[QFrame] = None,
        toast_type: str = "info",
        duration: int = 3000,
    ):
        super().__init__(parent)
        self.message = message
        self.toast_type = toast_type if toast_type in self._ICON else "info"
        self.duration = duration
        self._offset = 0

        self.setObjectName("Toast")
        self.setProperty("toastType", self.toast_type)

        self.setup_ui()
        self._repolish()
        self.setup_opacity_effect()
        self.start_animation()

    def setup_opacity_effect(self):
        """Setup opacity effect for fade animations (works on Wayland)."""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)

    def setup_ui(self):
        """Setup toast UI components."""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        self.icon_label = QLabel()
        self.icon_label.setObjectName("ToastIcon")
        self.icon_label.setProperty("toastType", self.toast_type)
        self.icon_label.setFixedSize(20, 20)
        self.icon_label.setText(self._ICON.get(self.toast_type, "ℹ"))
        layout.addWidget(self.icon_label)

        self.message_label = QLabel(self.message)
        self.message_label.setObjectName("ToastMessage")
        self.message_label.setWordWrap(True)
        self.message_label.setMaximumWidth(400)
        font = QFont()
        font.setPointSize(10)
        self.message_label.setFont(font)
        layout.addWidget(self.message_label)

        self.close_button = QLabel("✕")
        self.close_button.setObjectName("ToastClose")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.close_button.mousePressEvent = lambda e: self.close_toast()
        layout.addWidget(self.close_button)

        self.setMinimumWidth(300)
        self.adjustSize()

    def _repolish(self) -> None:
        for w in (self, self.icon_label, self.message_label, self.close_button):
            style = w.style()
            if style is not None:
                style.unpolish(w)
                style.polish(w)
            w.update()

    def paintEvent(self, event):
        """Custom paint for rounded corners and shadow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = QRectF(self.rect())
        path = QPainterPath()
        path.addRoundedRect(rect, 8, 8)

        shadow_color = QColor(0, 0, 0, 80)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(shadow_color))
        painter.drawPath(path.translated(0, 2))

        painter.setBrush(QBrush(self.palette().window()))
        painter.drawPath(path)

        super().paintEvent(event)

    @pyqtProperty(int)
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        if self.parent():
            parent_height = self.parent().height()
            if parent_height > 0:
                new_y = parent_height - self.height() - 20 - value
                new_y = max(0, new_y)
                self.move(self.x(), new_y)

    def start_animation(self):
        """Start animations."""
        self.show()

        self.fade_animation = QPropertyAnimation(
            self.opacity_effect, b"opacity"
        )
        self.fade_animation.setDuration(self.ANIMATION_DURATION)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.slide_animation = QPropertyAnimation(self, b"offset")
        self.slide_animation.setDuration(self.ANIMATION_DURATION)
        self.slide_animation.setStartValue(100)
        self.slide_animation.setEndValue(0)
        self.slide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.fade_animation.start()
        self.slide_animation.start()

        QTimer.singleShot(self.duration, self.fade_out)

    def fade_out(self):
        """Fade out animation."""
        self.fade_out_animation = QPropertyAnimation(
            self.opacity_effect, b"opacity"
        )
        self.fade_out_animation.setDuration(self.ANIMATION_DURATION)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_animation.finished.connect(self.close_toast)
        self.fade_out_animation.start()

    def close_toast(self):
        """Close the toast widget."""
        self.deleteLater()

    def enterEvent(self, event):
        """Pause auto-close on hover."""
        self.duration = 0

    def leaveEvent(self, event):
        """Resume auto-close on leave."""
        if self.duration == 0:
            QTimer.singleShot(self.DISPLAY_DURATION, self.fade_out)
