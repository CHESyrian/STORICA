"""
Warehouses tab for inventory management.
Includes navbar and paginated table for warehouse management.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

from frontend.models import GenericTableModel
from frontend.api import APIResult, AsyncExecutor
from frontend.ui.widgets import (
    Navbar, PaginatedTableView, LoadingOverlay
)
from frontend.utils.signals import signals
from frontend.utils.managers import MessageManager
from frontend.utils.dialog_handler import DialogHandler
from frontend.utils.constants import (
    Color, Icon, TimeOut, 
    WAREHOUSES_COLUMN_MAP, 
    WAREHOUSES_NAVBAR_COMPONENTS, 
)
from frontend.utils.config import DEFAULT_PAGE_SIZE

from frontend.controllers import WarehouseController

from frontend.ui.dialogs import (
    AddWarehouseDialog
)


class WarehouseTab(QWidget):
    """
    Warehouses management tab.
    Fixed tab that cannot be closed or removed.
    """

    warehouse_selected = pyqtSignal(dict)
    warehouse_added    = pyqtSignal(dict)
    warehouse_updated  = pyqtSignal(dict)
    warehouse_deleted  = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.controller     = WarehouseController()
        self.msg_manager    = MessageManager()
        self.executor       = AsyncExecutor()
        self.overlay        = LoadingOverlay(self)
        self.dialog_handler = DialogHandler(
            executor=self.executor,
            overlay=self.overlay,
            message_manager=self.msg_manager,
        )

        self._current_page   = None
        self._page_size      = DEFAULT_PAGE_SIZE
        self._current_row    = None
        self._last_filters   = None
        self._create_dialogs = {
            "warehouse": (
                AddWarehouseDialog,
                lambda self: (),
                self.controller.create_warehouse,
                "Warehouse",
            )
        }

        self.setup_ui()
        self.connect_signals()

        # Set toast parent for this widget
        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        """Setup the warehouses tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create navbar
        self.navbar = Navbar(self)

        # Create table model and view
        self.table_model = GenericTableModel(
            headers=list(WAREHOUSES_COLUMN_MAP.keys()),
            column_map=WAREHOUSES_COLUMN_MAP
        )
        self.table_view = PaginatedTableView(self.table_model)

        self._configure_navbar()

        layout.addWidget(self.navbar)
        layout.addWidget(self.table_view)

    def _configure_navbar(self):
        """Configure the navbar controls."""
        # Configure buttons
        self.navbar.configure_icon_button(
            self.navbar.button_1,
            "add_warehouse",
            Icon.FILE_PLUS_CORNER,
            Color.COLOR_GR02,
            "Add new warehouse"
        )

        # Show default setup (buttons 1-4, search, status, refresh)
        self.navbar.set_components_visible(WAREHOUSES_NAVBAR_COMPONENTS)

    def connect_signals(self):
        """Connect all signals."""
        # Navbar signals
        self.navbar.refresh_clicked.connect(self.refresh) 
        self.navbar.button_1_clicked.connect(self.add_dialog)

        # Table signals
        self.table_view.row_selected.connect(self.on_row_selected)
        self.table_view.page_changed.connect(self.on_page_changed)

    # ------------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------------

    def refresh(self):
        """Refresh the current page data."""
        self._current_page = 1
        self.load_data()

    def resizeEvent(self, event):
        super().resizeEvent(event)

        if self.overlay:
            self.overlay.setGeometry(self.rect())

    # -- Data loading ------------------------------------
    def load_data(self) -> None:
        """Called on init, refresh button, and after any write operation."""

        self.overlay.show_message("Loading warehouses...")

        self._last_filter = self.navbar.get_all_filters()

        self.executor.run(
            self.controller.load_warehouses,
            self._current_page,
            self._page_size,
            self._last_filter['search'],
            self._last_filter['status'],
            self._last_filter['active'],
            on_result=self._on_warehouses_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    # -- Dialogs -------------------------------------
    def add_dialog(self):
        """Open the add warehouse dialog."""
        self.open_create_dialog('warehouse')

    def open_create_dialog(self, name):
        dialog_cls, args_fn, create_fn, label = self._create_dialogs[name]
        
        dialog = dialog_cls(*args_fn(self))

        self.dialog_handler.open(
            dialog=dialog,
            create_fn=create_fn,
            entity_name=label,
        )

    # ------------------------------------------------------------------
    # Actions / Helpers / Handlers
    # ------------------------------------------------------------------

    # -- Row selection handlers -------------------
    def on_row_selected(self, row: dict):
        """Handle row selection."""
        self._current_row = row
        self.warehouse_selected.emit(row)

    # -- Page changing handlers -------------------
    def on_page_changed(self, page):
        self._current_page = page

    # -- Action handlers ---------------------------
    def get_selected_warehouse(self) -> dict | None:
        """Get the currently selected warehouse."""
        return self.table_view.get_selected_row()

    # -- Action handlers ---------------------------
    def get_row(self, row_index: int) -> dict | None:
        """Get specific row"""
        return self.table_view.get_row(row_index)

    # -- Action handlers ---------------------------
    def get_column(self, column_name: str, unique: bool = False) -> list:
        """Get specific column."""
        return self.table_view.get_column(column_name, unique) or []

    # -- Load Warehouses -----------------------------
    def _on_warehouses_loaded(self, result):
        if result.ok:
            warehouses = result.data.get('data', [])
            paginator = result.data.get('paginator', {})

            self._populate(warehouses, paginator)
            self.set_filters_options()
            self.handle_result(result)

    # -- Load Data to Table ------------------------
    def _populate(self, warehouses: list[dict], paginator: dict) -> None:
        self.table_view.set_data(warehouses, paginator)

    # -- Update Filters --------------------------------
    def set_filters_options(self) -> None:
        # Status Names
        status_names = {
            status_name: status_name
            for status_name in self.get_column('status', []) if status_name
        }
        self.navbar.set_status_items({"": "", **status_names})

    # -- Handle Worker Error -------------------------
    def _on_worker_error(self, error):
        self.msg_manager.error(
            f"{error['type']}",
            f"{error['message']} \n {error['traceback']}",
        )

    # -- Handle Worker Finished ----------------------
    def _on_worker_finished(self):
        self.overlay.hide()

    # -- Handle Worker Result----------------------
    def handle_result(
        self,
        result: APIResult,
    ):

        if result.ok:
            signals.statusbar_msg.emit(
                "Request Success, Data Loaded",
                TimeOut.TIMEOUT_5000,
                False
            )

        elif result.server_error:
            signals.statusbar_msg.emit(
                "Server unavailable — showing last loaded data.",
                TimeOut.TIMEOUT_5000,
                True
            )

        elif result.not_found:
            signals.statusbar_msg.emit(
                "No data found.",
                TimeOut.TIMEOUT_5000,
                False
            )

        else:
            signals.statusbar_msg.emit(
                f"Could not load warehouses: {result.error}",
                TimeOut.TIMEOUT_5000,
                True
            )