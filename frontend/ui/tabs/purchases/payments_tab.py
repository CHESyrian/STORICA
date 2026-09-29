"""
Payments management tab.
Includes navbar and paginated table for payment records.
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
    PURCHASES_PAYMENTS_COLUMN_MAP,
    PURCHASES_PAYMENTS_NAVBAR_COMPONENTS,
    PURCHASE_PAYMENT_DETAIL_COLUMN_MAP, 
)
from frontend.utils.config import DEFAULT_PAGE_SIZE

from frontend.ui.dialogs import (
    ShowDataDialog,
)

from frontend.controllers import PurchasesController


class PaymentsTab(QWidget):
    """
    Payments management tab.
    Fixed tab that cannot be closed or removed.
    """

    payment_selected = pyqtSignal(dict)
    payment_added    = pyqtSignal(dict)
    payment_updated  = pyqtSignal(dict)
    payment_deleted  = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.controller     = PurchasesController()
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
        self._returned_data  = None

        self.setup_ui()
        self.connect_signals()

        # Set toast parent for this widget
        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        """Setup the payments tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create navbar
        self.navbar = Navbar(self)

        # Create table model and view
        self.table_model = GenericTableModel(
            headers=list(PURCHASES_PAYMENTS_COLUMN_MAP.keys()),
            column_map=PURCHASES_PAYMENTS_COLUMN_MAP
        )
        self.table_view = PaginatedTableView(self.table_model)

        self._configure_navbar()

        layout.addWidget(self.navbar)
        layout.addWidget(self.table_view)

    def _configure_navbar(self):
        """Configure the navbar controls."""

        # Show default setup (buttons 1-4, search, status, refresh)
        # but we might want to hide status if not applicable
        self.navbar.set_components_visible(PURCHASES_PAYMENTS_NAVBAR_COMPONENTS)

    def connect_signals(self):
        """Connect all signals."""
        # Navbar signals
        self.navbar.refresh_clicked.connect(self.refresh)

        # Table signals
        self.table_view.row_selected.connect(self.on_row_selected)
        self.table_view.row_double_clicked.connect(self.show_payment_details)
        self.table_view.page_changed.connect(self.on_page_changed)

    # ------------------------------------------------------------------
    # Worker
    # ------------------------------------------------------------------

    def refresh(self):
        """Refresh the current page data."""
        self._current_page = 1
        self._current_row  = None
        self.load_data()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.overlay:
            self.overlay.setGeometry(self.rect())

    # -- Data loading ------------------------------------
    def get_all_data(self, model: str):
        """Fetch all records for a given model (for dropdowns)."""
        self.overlay.show()
        data = self.controller.get_all(model)
        self.overlay.hide()
        return data

    def get_current_payment_data(self):
        """Fetch full details of the currently selected payment."""
        self.overlay.show()
        payment_id = self._current_row['id']
        data = self.controller.get_purchase_payment(payment_id)
        self.overlay.hide()
        return data

    def load_data(self) -> None:
        """Called on init, refresh button, and after any write operation."""
        self.overlay.show_message("Loading payments...")

        self._last_filter = self.navbar.get_all_filters()

        self.executor.run(
            self.controller.load_purchase_payments,
            self._current_page,
            self._page_size,
            self._last_filter.get('search', '') or None,
            self._last_filter.get('status', '') or None,
            on_result=self._on_payments_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    # -- Dialogs -------------------------------------

    def show_payment_details(self, row: dict):
        """
        Open the read-only payment details dialog for a double-clicked row.
        Re-fetches the full record including items and notes.
        """
        self._current_row = row

        self.overlay.show_message("Loading payment details...")

        self.executor.run(
            self.controller.get_purchase_payment,
            row['id'],
            on_result=self._on_payment_details_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def _on_payment_details_loaded(self, result):
        if result.ok:
            dialog = ShowDataDialog(
                result.data.get('data', {}),
                PURCHASE_PAYMENT_DETAIL_COLUMN_MAP,
                None,
                f"Payment {self._current_row.get('code', '')} Details",
            )
            dialog.exec()
        else:
            self.msg_manager.error(
                'Could Not Load Payment',
                f"{result.error}",
            )

    # ------------------------------------------------------------------
    # Actions / Helpers / Handlers
    # ------------------------------------------------------------------

    # -- Row selection handlers -------------------
    def on_row_selected(self, row: dict):
        """Handle row selection."""
        self._current_row = row
        self.payment_selected.emit(row)

    # -- Page changing handlers -------------------
    def on_page_changed(self, page):
        self._current_page = page

    # -- Action handlers ---------------------------
    def get_selected_payment(self) -> dict | None:
        """Get the currently selected payment row."""
        return self.table_view.get_selected_row()

    def get_row(self, row_index: int) -> dict | None:
        """Get specific row by index."""
        return self.table_view.get_row(row_index)

    def get_column(self, column_name: str, unique: bool = False) -> list:
        """Get values from a specific column."""
        return self.table_view.get_column(column_name, unique) or []

    # -- Load Payments -----------------------------
    def _on_payments_loaded(self, result):
        if result.ok:
            payments = result.data.get('data', [])
            paginator = result.data.get('paginator', {})
            self._populate(payments, paginator)
            self.set_filters_options()
            self.handle_result(result)

    # -- Load Data to Table ------------------------
    def _populate(self, payments: list[dict], paginator: dict) -> None:
        self.table_view.set_data(payments, paginator)

    # -- Update Filters --------------------------------
    def set_filters_options(self) -> None:
        # Populate status filter dropdown with distinct statuses from data
        status_names = {
            status: status
            for status in self.get_column("status", unique=True) if status
        }
        self.navbar.set_status_items({"": "", **status_names})

    # -- Handle Worker Error -------------------------
    def _on_worker_error(self, error):
        self.msg_manager.error(
            f"{error.get('type', 'Error')}",
            f"{error.get('message', '')} \n {error.get('traceback', '')}",
        )

    # -- Handle Worker Finished ----------------------
    def _on_worker_finished(self):
        self.overlay.hide()

    # -- Handle Worker Result----------------------
    def handle_result(self, result: APIResult):
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
                f"Could not load payments: {result.error}",
                TimeOut.TIMEOUT_5000,
                True
            )