"""
About / Version dialog for STORICA.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
)

from frontend.utils.config import APP_NAME, APP_VERSION, ORG_NAME, API_BASE_URL


class AboutDialog(QDialog):
    """Simple About dialog showing app name, version, org, and API endpoint."""

    def __init__(self, parent=None, backend_status: str | None = None):
        super().__init__(parent)
        self.setWindowTitle(f"About {APP_NAME}")
        self.setFixedWidth(380)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 20)

        title = QLabel(APP_NAME)
        title.setObjectName("aboutTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)

        version = QLabel(f"Version {APP_VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version)

        org = QLabel(ORG_NAME)
        org.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(org)

        api = QLabel(f"API: {API_BASE_URL}")
        api.setAlignment(Qt.AlignmentFlag.AlignCenter)
        api.setWordWrap(True)
        layout.addWidget(api)

        if backend_status:
            status = QLabel(f"Backend: {backend_status}")
            status.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(status)

        layout.addSpacing(8)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
