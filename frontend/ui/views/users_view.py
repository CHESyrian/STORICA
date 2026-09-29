"""Users management page."""

from PyQt6.QtCore import pyqtSignal

from frontend.ui.widgets import StandardTabWidget
from frontend.ui.tabs.users.users_tab import UsersTab


class UsersView(StandardTabWidget):
    users_tab_selected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.users_tab = UsersTab()
        self.add_tab(
            self.users_tab,
            "👥 Users",
            closable=False,
            tooltip="Manage application users",
        )
