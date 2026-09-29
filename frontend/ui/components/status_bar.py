"""
Custom status bar component for STORICA.
"""
from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import QTimer


class StatusBar(QStatusBar):
    """Status bar with temporary messages and a live clock."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.temp_label: QLabel | None = None
        self._setup_ui()

    def _setup_ui(self):
        self.setObjectName("statusBar")
        self.setFixedHeight(35)

        self.permanent_label = QLabel("Ready")
        self.permanent_label.setProperty("info", True)
        self.addWidget(self.permanent_label, 1)

        self._timer = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._restore_permanent)

    def show_message(self, message: str, timeout: int = 5000, is_error: bool = False):
        """Show a temporary message that reverts after timeout."""
        if self.temp_label:
            self.removeWidget(self.temp_label)
            self.temp_label = None

        self.temp_label = QLabel(message)
        self.temp_label.setProperty("error" if is_error else "info", True)

        self.removeWidget(self.permanent_label)
        self.insertWidget(0, self.temp_label, 1)
        self._timer.start(timeout)

    def _restore_permanent(self):
        """Restore the permanent label after a temporary message expires."""
        if self.temp_label:
            self.removeWidget(self.temp_label)
            self.temp_label = None
        self.insertWidget(0, self.permanent_label, 1)

    def set_permanent_message(self, message: str, is_error: bool = False):
        """Set the persistent left-side status message."""
        self.permanent_label.setText(message)
        self.permanent_label.setProperty("error" if is_error else "info", True)
        self.permanent_label.style().polish(self.permanent_label)

    def clear_message(self):
        """Immediately clear any temporary message."""
        self._timer.stop()
        self._restore_permanent()
