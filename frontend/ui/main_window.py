"""
Main window for STORICA POS application.
Composed of modular components.
"""
from functools import partial

from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout
from PyQt6.QtCore import QTimer, pyqtSignal

from frontend.utils.signals import signals
from frontend.utils.managers import MessageManager
from frontend.utils.config import (
    APP_NAME,
)

from frontend.ui.components import (
    Sidebar, 
    StackContent, 
    StatusBar
)
from frontend.ui.dialogs.about_dialog import AboutDialog


class MainWindow(QMainWindow):
    """Main application window composed of modular components."""

    def __init__(self, auth_client):
        super().__init__()
        self.auth = auth_client
        self.setup_ui()
        self.connect_signals()
        self.load_user_info()
        # Periodic lightweight health probe (every 60s)
        self._health_timer = QTimer(self)
        self._health_timer.timeout.connect(self._probe_backend)
        self._health_timer.start(60_000)
        # Initial probe shortly after show
        QTimer.singleShot(1500, self._probe_backend)

    def setup_ui(self):
        """Setup the main window UI."""
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(900, 600)
        self.showMaximized()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setObjectName('centralWindow')

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = Sidebar()
        self.content_stack = StackContent()
        self.status_bar = StatusBar()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack, stretch=1)
        self.setStatusBar(self.status_bar)

        self.navigate_to("storica")


    def connect_signals(self):
        """Connect component signals."""
        self.sidebar.nav_clicked.connect(self.handle_navigation)
        if hasattr(self.sidebar, "about_clicked"):
            self.sidebar.about_clicked.connect(self.show_about)
        signals.statusbar_msg.connect(self.on_status_bar_message)
        signals.brand_clicked.connect(
            partial(self.navigate_to, "storica")
        )
        # Surface connection problems in the status bar
        self.auth.connection_error.connect(
            lambda msg: self.status_bar.show_message(msg, 5000, is_error=True)
        )

    def on_status_bar_message(self, msg, timeout, is_error):
        self.status_bar.show_message(msg, timeout, is_error)

    def handle_navigation(self, item_id: str):
        """Handle sidebar navigation clicks."""
        if item_id == "logout":
            self.handle_logout()
            return

        pages = {"inventory", "purchases", "sales", "users", "panel"}
        if item_id in pages:
            self.navigate_to(item_id)
            
        else:
            self.status_bar.show_message(
                f"Unknown navigation: {item_id}", 
                2000, 
                is_error=True
            )

    def navigate_to(self, page: str):
        """Switch to a page and sync sidebar and status bar."""
        self.content_stack.show_page(page)
        self.status_bar.show_message(page.capitalize())
        self.sidebar.set_active_item(page)

    def load_user_info(self):
        """Load and display user information."""
        try:
            user_data = self.auth.get_current_user()
            if user_data:
                username = user_data.get("username", "User")
                role = user_data.get("role", "")
                self.sidebar.set_user_info(username, role)
                self.status_bar.set_permanent_message(f"Welcome back, {username}")
        except Exception as e:
            self.status_bar.show_message(
                f"Failed to load user info: {e}", 
                3000, 
                is_error=True
            )

    def handle_logout(self):
        """Handle logout action."""
        if MessageManager().logout_confirmation(self):
            self.status_bar.show_message("Logging out...", 1000)
            QTimer.singleShot(500, self._perform_logout)

    def _perform_logout(self):
        """Perform actual logout after delay."""
        self.auth.logout()
        self.close()

    def show_about(self):
        """Show About dialog, including a live backend health status."""
        result = self.auth.health_check(timeout=2.0)
        if result.ok and isinstance(result.data, dict):
            backend_status = result.data.get("status", "ok")
            db = result.data.get("database", "?")
            status_text = f"{backend_status} (db: {db})"
        else:
            status_text = result.error or "unreachable"
        dlg = AboutDialog(self, backend_status=status_text)
        dlg.exec()

    def _probe_backend(self):
        """Background health probe — updates status bar on failure only."""
        result = self.auth.health_check(timeout=2.0)
        if not result.ok:
            self.status_bar.show_message(
                result.error or "Backend unreachable",
                4000,
                is_error=True,
            )

    def closeEvent(self, event):
        """Confirm before closing the application window."""
        if MessageManager().question(
            "Quit STORICA",
            "Close the application?",
            parent=self,
        ):
            event.accept()
        else:
            event.ignore()
