"""
Login dialog for STORICA.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QProgressBar, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from frontend.api.auth_client import AuthClient
from frontend.utils.config import APP_NAME
from frontend.utils.constants import (
    FontFamily, 
    FontSize, 
    Image
)
from frontend.ui.widgets import BrandWidget


class LoginDialog(QDialog):
    """Login dialog for manual credential entry."""

    def __init__(self):
        super().__init__()
        self.auth_client = AuthClient()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(480, 580)

        container = QFrame()
        container.setObjectName("loginContainer")

        layout = QVBoxLayout(container)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 50, 40, 50)

        width  = int(self.width())
        height = int(width / 3)
        self.brand_widget = BrandWidget(
            logo_path=Image.BRAND,
            width=width,
            height=height
        )

        subtitle = QLabel("Welcome back! Please login to continue")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setProperty("subtitle", True)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setMinimumHeight(40)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(40)

        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setChecked(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximum(0)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setTextVisible(False)

        self.login_btn = QPushButton("Login")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setProperty("secondary", True)
        self.cancel_btn.clicked.connect(self.reject)

        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.cancel_btn)

        layout.addWidget(self.brand_widget)
        layout.addWidget(subtitle)
        layout.addWidget(QLabel("Username"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Password"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.remember_checkbox)
        layout.addWidget(self.progress_bar)
        layout.addLayout(button_layout)
        layout.addWidget(self.status_label)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.addWidget(container)

        self.username_input.setFocus()
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        remember = self.remember_checkbox.isChecked()

        if not username or not password:
            self._show_status("Please enter username and password", is_error=True)
            return

        self._set_inputs_enabled(False)
        self.progress_bar.setVisible(True)
        self._show_status("Authenticating...")

        success, message = self.auth_client.login(username, password, remember)

        if success and self.auth_client.verify_token():
            self.accept()
            
        else:
            self._show_status(message or "Invalid credentials", is_error=True)
            self._set_inputs_enabled(True)
            self.progress_bar.setVisible(False)
            self.username_input.setFocus()

    def _show_status(self, message: str, is_error: bool = False):
        prefix = "⚠" if is_error else "ℹ"
        self.status_label.setText(f"{prefix} {message}")
        self.status_label.setProperty("error" if is_error else "info", True)
        self.status_label.style().polish(self.status_label)

    def _set_inputs_enabled(self, enabled: bool):
        for widget in (
            self.username_input, self.password_input,
            self.remember_checkbox, self.login_btn, self.cancel_btn
        ):
            widget.setEnabled(enabled)

            