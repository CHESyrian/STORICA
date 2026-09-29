"""
Loading overlay widget.

Styling lives in theme QSS (QWidget#LoadingOverlay, QLabel#LoadingOverlayLabel).
No setStyleSheet in this module.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

from .spinner import Spinner


class LoadingOverlay(QWidget):
    """Overlay widget with spinner and loading message."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("LoadingOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(16)

        self.spinner = Spinner(size=48)

        self.label = QLabel("Loading...")
        self.label.setObjectName("LoadingOverlayLabel")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(
            self.spinner,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )
        layout.addWidget(
            self.label,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        self.hide()

    def show_message(self, message: str = "Loading..."):
        self.label.setText(message)
        self.setGeometry(self.parent().rect())
        self.show()
        self.raise_()

    def hide_message(self):
        self.hide()

    def resizeEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)
