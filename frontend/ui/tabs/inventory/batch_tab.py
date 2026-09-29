"""
Batches tab for inventory management.
Includes navbar and paginated table for batch management.
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
    BATCHES_COLUMN_MAP,
    BATCHES_NAVBAR_COMPONENTS,
)
from frontend.utils.config import DEFAULT_PAGE_SIZE

from frontend.controllers import BatchController


class BatchTab(QWidget):
    """
    Batches management tab.
    Fixed tab that cannot be closed or removed.
    """

    batch_selected = pyqtSignal(dict)
    batch_added    = pyqtSignal(dict)
    batch_updated  = pyqtSignal(dict)
    batch_deleted  = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.controller     = BatchController()
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

        self.setup_ui()
        self.connect_signals()

        # Set toast parent for this widget
        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        """Setup the batches tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create navbar
        self.navbar = Navbar(self)

        # Create table model and view
        self.table_model = GenericTableModel(
            headers=list(BATCHES_COLUMN_MAP.keys()),
            column_map=BATCHES_COLUMN_MAP
        )
        self.table_view = PaginatedTableView(self.table_model, stretch=False)

        self._configure_navbar()

        layout.addWidget(self.navbar)
        layout.addWidget(self.table_view)

    def _configure_navbar(self):
        """Batches are created automatically when posting purchase invoices."""
        self.navbar.set_components_visible(BATCHES_NAVBAR_COMPONENTS)

    def connect_signals(self):
        """Connect all signals."""
        self.navbar.refresh_clicked.connect(self.refresh)

        self.table_view.row_selected.connect(self.on_row_selected)
        self.table_view.page_changed.connect(self.on_page_changed)

    def get_all_data(self, model: str):
        self.overlay.show()
        data = self.controller.get_all(model)
        self.overlay.hide()
        return data


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

        self.overlay.show_message("Loading batches...")

        self._last_filter = self.navbar.get_all_filters()

        self.executor.run(
            self.controller.load_batches,
            self._current_page,
            self._page_size,
            self._last_filter.get('search'),
            self._last_filter.get('status'),
            self._last_filter.get('choice'), 
            self._last_filter.get('active'),
            on_result=self._on_batches_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    # ------------------------------------------------------------------
    # Actions / Helpers / Handlers
    # ------------------------------------------------------------------

    # -- Row selection handlers -------------------
    def on_row_selected(self, row: dict):
        """Handle row selection."""
        self._current_row = row
        self.batch_selected.emit(row)

    # -- Page changing handlers -------------------
    def on_page_changed(self, page):
        self._current_page = page

    # -- Action handlers ---------------------------
    def get_selected_batch(self) -> dict | None:
        """Get the currently selected batch."""
        return self.table_view.get_selected_row()

    # -- Action handlers ---------------------------
    def get_row(self, row_index: int) -> dict | None:
        """Get specific row"""
        return self.table_view.get_row(row_index)

    # -- Action handlers ---------------------------
    def get_column(self, column_name: str, unique: bool = False) -> list:
        """Get specific column."""
        return self.table_view.get_column(column_name, unique) or []

    # -- Load Batches -----------------------------
    def _on_batches_loaded(self, result):
        if result.ok:
            batches = result.data.get('data', [])
            paginator = result.data.get('paginator', {})

            self._populate(batches, paginator)
            self.set_filters_options()
            self.handle_result(result)

    # -- Load Data to Table ------------------------
    def _populate(self, batches: list[dict], paginator: dict) -> None:
        self.table_view.set_data(batches, paginator)

    # -- Update Filters --------------------------------
    def set_filters_options(self) -> None:
        # Get unique variant options for the status dropdown
        #variant_names = self.get_column("variant_sku", [])
        #variant_ids = self.get_column("variant", [])
        #
        #variant_options = {
        #    variant_id: variant_name
        #    for variant_id, variant_name in zip(variant_ids, variant_names) 
        #    if variant_id and variant_name
        #}
        #self.navbar.set_status_items({"": "", **variant_options})
        
        # Get unique status options for the status dropdown
        status_values = self.get_column("status", unique=True)
        status_options = {
            status: status.replace("_", " ").title() 
            for status in status_values if status
        }
        self.navbar.set_status_items({"": "", **status_options})

        # Get unique warehouse options for choice dropdown
        warehouse_names = self.get_column("warehouse_name", [])
        warehouse_ids = self.get_column("warehouse", [])
        
        warehouse_options = {
            warehouse_id: warehouse_name
            for warehouse_id, warehouse_name in zip(warehouse_ids, warehouse_names) 
            if warehouse_id and warehouse_name
        }
        self.navbar.set_choice_items({"": "", **warehouse_options})            

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
                f"Could not load batches: {result.error}",
                TimeOut.TIMEOUT_5000,
                True
            )
