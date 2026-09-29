"""Users admin tab."""

from __future__ import annotations

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

from frontend.models import GenericTableModel
from frontend.api import AsyncExecutor
from frontend.ui.widgets import Navbar, PaginatedTableView, LoadingOverlay
from frontend.utils.managers import MessageManager
from frontend.utils.dialog_handler import DialogHandler
from frontend.utils.constants import (
    Color, Icon,
    USERS_COLUMN_MAP,
    USERS_NAVBAR_COMPONENTS,
)
from frontend.utils.config import DEFAULT_PAGE_SIZE

from frontend.controllers.users.user_controller import UserController
from frontend.ui.dialogs.users_dialogs.user_dialog import (
    AddUserDialog,
    EditUserDialog,
    ResetPasswordDialog,
)


class UsersTab(QWidget):
    """Admin users management tab."""

    user_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.controller = UserController()
        self.msg_manager = MessageManager()
        self.executor = AsyncExecutor()
        self.overlay = LoadingOverlay(self)
        self.dialog_handler = DialogHandler(
            executor=self.executor,
            overlay=self.overlay,
            message_manager=self.msg_manager,
        )
        self._current_page = 1
        self._page_size = DEFAULT_PAGE_SIZE
        self._current_row = None

        self.setup_ui()
        self.connect_signals()
        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.navbar = Navbar(self)
        self.table_model = GenericTableModel(
            headers=list(USERS_COLUMN_MAP.keys()),
            column_map=USERS_COLUMN_MAP,
        )
        self.table_view = PaginatedTableView(self.table_model)
        self._configure_navbar()
        layout.addWidget(self.navbar)
        layout.addWidget(self.table_view)

    def _configure_navbar(self):
        self.navbar.configure_icon_button(
            self.navbar.button_1,
            "add_user",
            Icon.FILE_PLUS_CORNER,
            Color.COLOR_GR02,
            "Add user",
        )
        self.navbar.configure_icon_button(
            self.navbar.button_2,
            "edit_user",
            Icon.FILE_PEN_LINE,
            Color.COLOR_PU02,
            "Edit user",
        )
        self.navbar.configure_icon_button(
            self.navbar.button_3,
            "deactivate_user",
            Icon.TRASH_2,
            Color.COLOR_RE02,
            "Deactivate user",
        )
        self.navbar.configure_icon_button(
            self.navbar.button_4,
            "reset_password",
            Icon.REFRESH_CCW_DOT,
            Color.COLOR_YE02,
            "Reset password",
        )
        # choice filter = role
        self.navbar.set_choice_items(
            {
                "": "All roles",
                "admin": "Administrator",
                "manager": "Manager",
                "user": "User",
                "viewer": "Viewer",
                "guest": "Guest",
            }
        )
        self.navbar.set_components_visible(USERS_NAVBAR_COMPONENTS)

    def connect_signals(self):
        self.navbar.refresh_clicked.connect(self.refresh)
        self.navbar.button_1_clicked.connect(self.add_user)
        self.navbar.button_2_clicked.connect(self.edit_user)
        self.navbar.button_3_clicked.connect(self.deactivate_user)
        self.navbar.button_4_clicked.connect(self.reset_password)
        self.navbar.choice_changed.connect(lambda _=None: self.refresh())
        self.navbar.active_changed.connect(lambda _=None: self.refresh())
        self.table_view.row_selected.connect(self.on_row_selected)
        self.table_view.page_changed.connect(self.on_page_changed)

    def refresh(self):
        self._current_page = 1
        self.load_data()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.overlay:
            self.overlay.setGeometry(self.rect())

    def load_data(self) -> None:
        self.overlay.show_message("Loading users...")
        filters = self.navbar.get_all_filters()
        self.executor.run(
            self.controller.load_users,
            self._current_page,
            self._page_size,
            filters.get("search"),
            filters.get("choice"),
            filters.get("active"),
            on_result=self._on_loaded,
            on_error=self._on_error,
            on_finished=lambda: self.overlay.hide(),
        )

    def _on_loaded(self, result):
        if not result.ok:
            self.msg_manager.error(
                "Load failed", result.error or "Unknown error"
            )
            return

        payload = result.data or {}
        if not isinstance(payload, dict):
            payload = {}

        # Standard ApiResponse: {"data": [...], "paginator": {...}}
        rows = payload.get("data")
        paginator = payload.get("paginator") or {}

        # Fallbacks for other shapes (DRF page or bare list)
        if rows is None:
            if isinstance(payload.get("results"), list):
                rows = payload["results"]
                paginator = {
                    "count": payload.get("count"),
                    "page": payload.get("page") or self._current_page,
                    "page_size": payload.get("page_size") or self._page_size,
                }
            else:
                rows = []
        elif not isinstance(rows, list):
            # Nested page object under "data"
            if isinstance(rows, dict):
                paginator = rows.get("paginator") or paginator
                rows = rows.get("results") or rows.get("data") or []
            else:
                rows = []

        if hasattr(self.table_view, "set_data"):
            self.table_view.set_data(rows, paginator)
        else:
            self.table_model.set_rows(rows)
            count = paginator.get("count")
            if count is not None and hasattr(self.table_view, "set_total_count"):
                self.table_view.set_total_count(count)

    def _on_error(self, err):
        self.msg_manager.error("Error", str(err))

    def on_row_selected(self, row: dict):
        self._current_row = row
        self.user_selected.emit(row)

    def on_page_changed(self, page: int):
        self._current_page = page
        self.load_data()

    def _selected(self) -> dict | None:
        if self._current_row:
            return self._current_row
        self.msg_manager.warning("No Selection", "Please select a user.")
        return None

    def add_user(self):
        dlg = AddUserDialog()
        if not hasattr(dlg, "validate"):
            pass
        # Connect save via dialog_handler pattern if available
        def _submit():
            ok, msg = dlg.validate() if hasattr(dlg, "validate") else (True, "")
            if not ok:
                self.msg_manager.warning("Validation", msg)
                return
            data = dlg.get_data()
            self.overlay.show_message("Creating user...")
            self.executor.run(
                self.controller.create_user,
                data,
                on_result=lambda r: self._after_write(r, dlg, "User created"),
                on_error=self._on_error,
                on_finished=lambda: self.overlay.hide(),
            )

        dlg.save_btn.clicked.connect(_submit)
        dlg.exec()

    def edit_user(self):
        row = self._selected()
        if not row:
            return
        dlg = EditUserDialog(row)

        def _submit():
            data = dlg.get_data()
            self.overlay.show_message("Updating user...")
            self.executor.run(
                self.controller.update_user,
                row["id"],
                data,
                on_result=lambda r: self._after_write(r, dlg, "User updated"),
                on_error=self._on_error,
                on_finished=lambda: self.overlay.hide(),
            )

        dlg.save_btn.clicked.connect(_submit)
        dlg.exec()

    def deactivate_user(self):
        row = self._selected()
        if not row:
            return
        self.overlay.show_message("Deactivating...")
        self.executor.run(
            self.controller.deactivate_user,
            row["id"],
            on_result=lambda r: self._after_write(r, None, "User deactivated"),
            on_error=self._on_error,
            on_finished=lambda: self.overlay.hide(),
        )

    def reset_password(self):
        row = self._selected()
        if not row:
            return
        dlg = ResetPasswordDialog(row.get("username", ""))

        def _submit():
            ok, msg = dlg.validate()
            if not ok:
                self.msg_manager.warning("Validation", msg)
                return
            pw = dlg.get_data()["new_password"]
            self.overlay.show_message("Resetting password...")
            self.executor.run(
                self.controller.reset_password,
                row["id"],
                pw,
                on_result=lambda r: self._after_write(r, dlg, "Password reset"),
                on_error=self._on_error,
                on_finished=lambda: self.overlay.hide(),
            )

        dlg.save_btn.clicked.connect(_submit)
        dlg.exec()

    def _after_write(self, result, dlg, success_msg: str):
        if result.ok:
            self.msg_manager.success("Success", success_msg)
            if dlg is not None:
                dlg.accept()
            self.load_data()
        else:
            self.msg_manager.error("Failed", result.error or "Request failed")
