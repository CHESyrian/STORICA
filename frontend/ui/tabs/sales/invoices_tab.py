"""
Sales Invoices tab for sales management.
Includes navbar and paginated table for sales invoice management.

Mirrors purchases/invoices_tab.py exactly, with the counterparty and
filter wiring swapped from supplier/purchase -> customer/sale. Like
its purchasing twin, this tab has no create button — invoices are
only ever raised from SalesOrderTab against a selected order.
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
    SALES_INVOICES_COLUMN_MAP,
    SALES_INVOICES_NAVBAR_COMPONENTS,
)
from frontend.utils.config import DEFAULT_PAGE_SIZE
from frontend.ui.dialogs import AddSalesPaymentDialog

from frontend.controllers import SalesController


class SalesInvoiceTab(QWidget):
    """
    Sales Invoices management tab.
    Fixed tab that cannot be closed or removed.
    """

    sales_invoice_selected = pyqtSignal(dict)
    sales_invoice_added    = pyqtSignal(dict)
    sales_invoice_updated  = pyqtSignal(dict)
    sales_invoice_deleted  = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.controller     = SalesController()
        self.msg_manager    = MessageManager()
        self.executor       = AsyncExecutor()
        self.overlay        = LoadingOverlay(self)
        self.dialog_handler = DialogHandler(
            executor=self.executor,
            overlay=self.overlay,
            message_manager=self.msg_manager,
        )
        self._create_dialogs = {
            "sales_payment": (
                AddSalesPaymentDialog,
                lambda self: (
                    self.get_current_invoice_data().data.get("data"),
                ),
                self.controller.create_sales_payment,
                "Sales Payment",
            ),
        }

        self._current_page   = None
        self._page_size      = DEFAULT_PAGE_SIZE
        self._current_row    = None
        self._last_filters   = None

        self.setup_ui()
        self.connect_signals()

        # Set toast parent for this widget
        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        """Setup the sales invoices tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create navbar
        self.navbar = Navbar(self)

        # Create table model and view
        self.table_model = GenericTableModel(
            headers=list(SALES_INVOICES_COLUMN_MAP.keys()),
            column_map=SALES_INVOICES_COLUMN_MAP
        )
        self.table_view = PaginatedTableView(self.table_model)

        self._configure_navbar()

        layout.addWidget(self.navbar)
        layout.addWidget(self.table_view)

    def _configure_navbar(self):
        """Configure the navbar controls."""
        self.navbar.configure_icon_button(
            self.navbar.button_1,
            "add_sales_payment",
            Icon.FILE_PLUS_CORNER,
            Color.COLOR_PI09,
            "Add payment for selected invoice",
        )
        self.navbar.configure_icon_button(
            self.navbar.button_2,
            "post_sales_invoice",
            Icon.SEND,
            Color.COLOR_BU06,
            "Post selected draft invoice (FIFO stock-out)",
        )
        self.navbar.configure_icon_button(
            self.navbar.button_3,
            "cancel_sales_invoice",
            Icon.CIRCLE_X,
            Color.COLOR_RE02,
            "Cancel selected invoice",
        )
        self.navbar.set_components_visible(SALES_INVOICES_NAVBAR_COMPONENTS)

    def connect_signals(self):
        """Connect all signals."""
        self.navbar.refresh_clicked.connect(self.refresh)
        self.navbar.button_1_clicked.connect(self.add_payment_dialog)
        self.navbar.button_2_clicked.connect(self.post_selected)
        self.navbar.button_3_clicked.connect(self.cancel_selected)

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
    def get_all_data(self, model: str):
        self.overlay.show()
        data = self.controller.get_all(model)
        self.overlay.hide()

        return data

    def get_current_invoice_data(self):
        self.overlay.show()
        invoice_id = self._current_row["id"]
        data = self.controller.get_sales_invoice(invoice_id)
        self.overlay.hide()
        return data

    def add_payment_dialog(self):
        """Open add sales payment dialog for the selected invoice."""
        if self._current_row:
            self.open_create_dialog("sales_payment")
            self.refresh()
        else:
            self.msg_manager.error(
                "Empty Invoice",
                "Please select an invoice from the table.",
            )

    def post_selected(self):
        """Post the selected draft invoice (FIFO stock-out)."""
        row = self.get_selected_sales_invoice()
        if not row:
            self.msg_manager.warning(
                "No selection",
                "Select a draft invoice to post.",
            )
            return

        status = (row.get("status") or "").lower()
        if status != "draft":
            self.msg_manager.warning(
                "Not draft",
                f"Only DRAFT invoices can be posted "
                f"(current status: {row.get('status', '?')}).",
            )
            return

        invoice_id = row.get("id")
        label = row.get("code") or invoice_id
        if not self.msg_manager.question(
            "Post invoice",
            f"Post invoice {label}? This allocates stock (FIFO) "
            f"and cannot be easily undone.",
        ):
            return

        self.overlay.show_message("Posting invoice...")
        self.executor.run(
            self.controller.post_sales_invoice,
            invoice_id,
            on_result=self._on_action_result,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def cancel_selected(self):
        """Cancel the selected draft or unpaid sent invoice."""
        row = self.get_selected_sales_invoice()
        if not row:
            self.msg_manager.warning(
                "No selection",
                "Select an invoice to cancel.",
            )
            return

        status = (row.get("status") or "").lower()
        if status not in {"draft", "sent"}:
            self.msg_manager.warning(
                "Cannot cancel",
                f"Invoices with status '{row.get('status', '?')}' "
                f"cannot be cancelled from here.",
            )
            return

        invoice_id = row.get("id")
        label = row.get("code") or invoice_id
        if not self.msg_manager.question(
            "Cancel invoice",
            f"Cancel invoice {label}?",
        ):
            return

        self.overlay.show_message("Cancelling invoice...")
        self.executor.run(
            self.controller.cancel_sales_invoice,
            invoice_id,
            on_result=self._on_action_result,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def _on_action_result(self, result: APIResult):
        if result.ok:
            signals.statusbar_msg.emit(
                "Invoice updated successfully.",
                TimeOut.TIMEOUT_5000,
                False,
            )
            self.refresh()
        else:
            self.msg_manager.error(
                "Action failed",
                str(result.error or "Unknown error"),
            )

    def open_create_dialog(self, name):
        dialog_cls, args_fn, create_fn, label = self._create_dialogs[name]
        dialog = dialog_cls(*args_fn(self))
        self.dialog_handler.open(
            dialog=dialog,
            create_fn=create_fn,
            entity_name=label,
        )

    def load_data(self) -> None:
        """Called on init, refresh button, and after any write operation."""

        self.overlay.show_message("Loading sales invoices...")

        self._last_filter = self.navbar.get_all_filters()

        self.executor.run(
            self.controller.load_sales_invoices,
            self._current_page,
            self._page_size,
            self._last_filter['search'],
            self._last_filter['choice'],
            self._last_filter['active'],
            on_result=self._on_sales_invoices_loaded,
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
        self.sales_invoice_selected.emit(row)

    # -- Page changing handlers -------------------
    def on_page_changed(self, page):
        self._current_page = page

    # -- Action handlers ---------------------------
    def get_selected_sales_invoice(self) -> dict | None:
        """Get the currently selected sales invoice."""
        return self.table_view.get_selected_row()

    # -- Action handlers ---------------------------
    def get_row(self, row_index: int) -> dict | None:
        """Get specific row"""
        return self.table_view.get_row(row_index)

    # -- Action handlers ---------------------------
    def get_column(self, column_name: str, unique: bool = False) -> list:
        """Get specific column."""
        return self.table_view.get_column(column_name, unique) or []

    # -- Load Sales Invoices -----------------------------
    def _on_sales_invoices_loaded(self, result):
        if result.ok:
            sales_invoices = result.data.get('data', [])
            paginator = result.data.get('paginator', {})

            self._populate(sales_invoices, paginator)
            self.set_filters_options()
            self.handle_result(result)

    # -- Load Data to Table ------------------------
    def _populate(self, sales_invoices: list[dict], paginator: dict) -> None:
        self.table_view.set_data(sales_invoices, paginator)

    # -- Update Filters --------------------------------
    def set_filters_options(self) -> None:
        # SO numbers
        so_numbers = self.get_column("so_number", [])
        so_ids = self.get_column("order", [])

        so_options = {
            so_id: so_number
            for so_id, so_number in zip(so_ids, so_numbers) if so_id
        }
        self.navbar.set_choice_items({"": "", **so_options})

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
                f"Could not load sales invoices: {result.error}",
                TimeOut.TIMEOUT_5000,
                True
            )
