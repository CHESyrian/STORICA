"""
Purchase Invoices tab for purchases management.
Includes navbar and paginated table for purchase invoice management.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal

from frontend.models import GenericTableModel
from frontend.api import APIResult, AsyncExecutor
from frontend.controllers import PurchasesController

from frontend.ui.widgets import (
    Navbar, PaginatedTableView, LoadingOverlay
)
from frontend.ui.dialogs import (
    AddPurchasePaymentDialog,
    ShowDataDialog, 
)

from frontend.utils.signals import signals
from frontend.utils.managers import MessageManager
from frontend.utils.dialog_handler import DialogHandler
from frontend.utils.config import DEFAULT_PAGE_SIZE
from frontend.utils.constants import (
    Color, Icon, TimeOut, 
    INVOICE_STATUS, 
    PURCHASES_INVOICES_COLUMN_MAP, 
    PURCHASES_INVOICES_NAVBAR_COMPONENTS, 
    PURCHASE_INVOICE_DETAIL_FIELDS, 
    PURCHASE_INVOICE_ITEMS_COLUMN_MAP,
)


class PurchasesInvoiceTab(QWidget):
    """
    Purchase Invoices management tab.
    Fixed tab that cannot be closed or removed.
    """

    purchase_invoice_selected = pyqtSignal(dict)
    purchase_invoice_added    = pyqtSignal(dict)
    purchase_invoice_updated  = pyqtSignal(dict)
    purchase_invoice_deleted  = pyqtSignal(int)

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
        self._create_dialogs = {
            "purchase_payment": (
                AddPurchasePaymentDialog,
                lambda self: (
                    self.get_current_invoice_data().data.get('data'),
                ),
                self.controller.create_purchase_payment,
                "Pay for Purchase",
            ), 
        }

        self.setup_ui()
        self.connect_signals()

        # Set toast parent for this widget
        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        """Setup the purchase invoices tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)


        # Create navbar
        self.navbar = Navbar(self)

        # Create table model and view
        self.table_model = GenericTableModel(
            headers=list(PURCHASES_INVOICES_COLUMN_MAP.keys()),
            column_map=PURCHASES_INVOICES_COLUMN_MAP
        )
        self.table_view = PaginatedTableView(self.table_model)

        self._configure_navbar()

        layout.addWidget(self.navbar)
        layout.addWidget(self.table_view)

    def _configure_navbar(self):
        """Configure the navbar controls."""
        self.navbar.configure_icon_button(
            self.navbar.button_1,
            "add_purchase_payment",
            Icon.FILE_PLUS_CORNER,
            Color.COLOR_PI09,
            "Add payment for selected invoice",
        )
        self.navbar.configure_icon_button(
            self.navbar.button_2,
            "cancel_purchase_invoice",
            Icon.CIRCLE_X,
            Color.COLOR_RE02,
            "Cancel selected unpaid invoice (reverses received stock)",
        )
        self.navbar.set_components_visible(PURCHASES_INVOICES_NAVBAR_COMPONENTS)

    def connect_signals(self):
        """Connect all signals."""
        self.navbar.refresh_clicked.connect(self.refresh)
        self.navbar.button_1_clicked.connect(self.add_payment_dialog)
        self.navbar.button_2_clicked.connect(self.cancel_selected)

        self.table_view.row_selected.connect(self.on_row_selected)
        self.table_view.row_double_clicked.connect(self.show_invoice_details)
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
        self.overlay.show()
        data = self.controller.get_all(model)
        self.overlay.hide()

        return data

    def get_current_invoice_data(self):
        self.overlay.show()
        invoice_id = self._current_row['id']
        data = self.controller.get_purchase_invoice(invoice_id)
        self.overlay.hide()

        return data

    def load_data(self) -> None:
        """Called on init, refresh button, and after any write operation."""

        self.overlay.show_message("Loading purchase invoices...")

        self._last_filter = self.navbar.get_all_filters()

        self.executor.run(
            self.controller.load_purchase_invoices,
            self._current_page,
            self._page_size,
            self._last_filter['search'],
            self._last_filter['choice'],
            self._last_filter['active'],
            on_result=self._on_purchase_invoices_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    # -- Dialogs -------------------------------------
    def add_payment_dialog(self):
        """Open the add purchase payment dialog."""
        if self._current_row:
            self.open_create_dialog('purchase_payment')
        else:
            self.msg_manager.error(
                'Empty Invoice',
                'Please select an invoice from the table.',
            )

    def cancel_selected(self):
        """Cancel selected unpaid purchase invoice and reverse stock."""
        row = self.table_view.get_selected_row()
        if not row:
            self.msg_manager.warning(
                "No selection",
                "Select an unpaid invoice to cancel.",
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
            f"Cancel invoice {label}? Received stock will be reversed.",
        ):
            return
        self.overlay.show_message("Cancelling invoice...")
        self.executor.run(
            self.controller.cancel_purchase_invoice,
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

    def show_invoice_details(self, row: dict):
        """
        Open the read-only invoice details dialog for a double-clicked row.

        The table row only carries the list columns (PURCHASES_INVOICES_
        COLUMN_MAP), so this re-fetches the full record - including
        items, notes, and audit fields - before displaying it. Runs on
        the AsyncExecutor so a slow fetch doesn't freeze the UI.
        """
        self._current_row = row

        self.overlay.show_message("Loading invoice details...")

        self.executor.run(
            self.controller.get_purchase_invoice,
            row['id'],
            on_result=self._on_invoice_details_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def _on_invoice_details_loaded(self, result):
        if result.ok:
            dialog = ShowDataDialog(
                result.data.get('data', {}), 
                PURCHASE_INVOICE_DETAIL_FIELDS, 
                PURCHASE_INVOICE_ITEMS_COLUMN_MAP,
                f"Invoice {self._current_row['code']} Detailes"
            )
            dialog.exec()
        else:
            self.msg_manager.error(
                'Could Not Load Invoice',
                f"{result.error}",
            )

    # ------------------------------------------------------------------
    # Actions / Helpers / Handlers
    # ------------------------------------------------------------------

    # -- Row selection handlers -------------------
    def on_row_selected(self, row: dict):
        """Handle row selection."""
        self._current_row = row
        self.purchase_invoice_selected.emit(row)

    # -- Page changing handlers -------------------
    def on_page_changed(self, page):
        self._current_page = page

    # -- Action handlers ---------------------------
    def get_selected_purchase_invoice(self) -> dict | None:
        """Get the currently selected purchase invoice."""
        return self.table_view.get_selected_row()

    # -- Action handlers ---------------------------
    def get_row(self, row_index: int) -> dict | None:
        """Get specific row"""
        return self.table_view.get_row(row_index)

    # -- Action handlers ---------------------------
    def get_column(self, column_name: str, unique: bool = False) -> list:
        """Get specific column."""
        return self.table_view.get_column(column_name, unique) or []

    # -- Load Purchase Invoices -----------------------------
    def _on_purchase_invoices_loaded(self, result):
        if result.ok:
            purchase_invoices = result.data.get('data', [])
            paginator = result.data.get('paginator', {})

            self._populate(purchase_invoices, paginator)
            self.set_filters_options()
            self.handle_result(result)

    def _on_return_data(self, result):
        if result.ok:
            self._returned_data = result.data.get('data', [])

    # -- Load Data to Table ------------------------
    def _populate(self, purchase_invoices: list[dict], paginator: dict) -> None:
        self.table_view.set_data(purchase_invoices, paginator)

    # -- Update Filters --------------------------------
    def set_filters_options(self) -> None:
        # PO numbers
        po_numbers = self.get_column("po_number", [])
        po_ids = self.get_column("purchase_order", [])

        po_options = {
            po_id: po_number
            for po_id, po_number in zip(po_ids, po_numbers) if po_id
        }
        self.navbar.set_choice_items({"": "", **po_options})

    # -- Handle Worker Error -------------------------
    def _on_worker_error(self, error):
        self.msg_manager.error(
            f"{error['type']} \n", 
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
                f"Could not load purchase invoices: {result.error}",
                TimeOut.TIMEOUT_5000,
                True
            )