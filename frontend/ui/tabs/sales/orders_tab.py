"""
Sales Orders tab for sales management.
Includes navbar and paginated table for sales order management.

Mirrors purchases/orders_tab.py exactly, with the counterparty and
create-dialog wiring swapped from supplier/purchase -> customer/sale.
See that file for the purchasing-side twin.
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
    SALES_ORDERS_COLUMN_MAP,
    SALES_ORDERS_NAVBAR_COMPONENTS,
)
from frontend.utils.config import DEFAULT_PAGE_SIZE

from frontend.ui.dialogs import (
    AddSalesOrderDialog,
    AddSalesInvoiceDialog
)

from frontend.controllers import SalesController


class SalesOrderTab(QWidget):
    """
    Sales Orders management tab.
    Fixed tab that cannot be closed or removed.
    """

    sales_order_selected = pyqtSignal(dict)
    sales_order_added    = pyqtSignal(dict)
    sales_order_updated  = pyqtSignal(dict)
    sales_order_deleted  = pyqtSignal(int)

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

        self._current_page   = None
        self._page_size      = DEFAULT_PAGE_SIZE
        self._current_row    = None
        self._last_filters   = None
        self._returned_data  = None
        self._create_dialogs = {
            "sales_order": (
                AddSalesOrderDialog,
                lambda self: (
                    self.get_all_data("customers").data['data'],
                    self.get_all_data("variants").data['data'],
                ),
                self.controller.create_sales_order,
                "Add Sales Order",
            ),
            "sales_invoice": (
                AddSalesInvoiceDialog,
                lambda self: (
                    self.get_current_order_data().data['data'],
                ),
                self.controller.create_sales_invoice,
                "Add Sales Invoice",
            )
        }

        self.setup_ui()
        self.connect_signals()

        # Set toast parent for this widget
        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        """Setup the sales orders tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create navbar
        self.navbar = Navbar(self)

        # Create table model and view
        self.table_model = GenericTableModel(
            headers=list(SALES_ORDERS_COLUMN_MAP.keys()),
            column_map=SALES_ORDERS_COLUMN_MAP
        )
        self.table_view = PaginatedTableView(self.table_model)

        self._configure_navbar()

        layout.addWidget(self.navbar)
        layout.addWidget(self.table_view)

    def _configure_navbar(self):
        """Configure the navbar controls."""
        self.navbar.configure_icon_button(
            self.navbar.button_1,
            "add_sales_order",
            Icon.FILE_PLUS_CORNER,
            Color.COLOR_GR02,
            "Add new sales order",
        )
        self.navbar.configure_icon_button(
            self.navbar.button_2,
            "add_sales_invoice",
            Icon.FILE_PLUS_CORNER,
            Color.COLOR_YE02,
            "Create invoice from selected order",
        )
        self.navbar.configure_icon_button(
            self.navbar.button_3,
            "confirm_sales_order",
            Icon.SEND,
            Color.COLOR_BU06,
            "Confirm selected draft order",
        )
        self.navbar.configure_icon_button(
            self.navbar.button_4,
            "cancel_sales_order",
            Icon.CIRCLE_X,
            Color.COLOR_RE02,
            "Cancel selected order",
        )

        self.navbar.set_components_visible(SALES_ORDERS_NAVBAR_COMPONENTS)

    def connect_signals(self):
        """Connect all signals."""
        self.navbar.refresh_clicked.connect(self.refresh)
        self.navbar.button_1_clicked.connect(self.add_order_dialog)
        self.navbar.button_2_clicked.connect(self.add_invoice_dialog)
        self.navbar.button_3_clicked.connect(self.confirm_selected)
        self.navbar.button_4_clicked.connect(self.cancel_selected)

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

    def get_current_order_data(self):
        self.overlay.show()
        order_id = self._current_row['id']
        data = self.controller.get_sales_order(order_id)
        self.overlay.hide()

        return data

    def load_data(self) -> None:
        """Called on init, refresh button, and after any write operation."""

        self.overlay.show_message("Loading sales orders...")

        self._last_filter = self.navbar.get_all_filters()

        self.executor.run(
            self.controller.load_sales_orders,
            self._current_page,
            self._page_size,
            self._last_filter['search'],
            self._last_filter['status'],
            self._last_filter['active'],
            on_result=self._on_sales_orders_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    # -- Dialogs -------------------------------------
    def add_order_dialog(self):
        """Open the add sales order dialog."""
        self.open_create_dialog('sales_order')

    def add_invoice_dialog(self):
        """Open the add sales invoice dialog (order must not be draft)."""
        if not self._current_row:
            self.msg_manager.error(
                'Empty Order',
                'Please select an order from the table.',
            )
            return
        status = (self._current_row.get("status") or "").lower()
        if status == "draft":
            self.msg_manager.warning(
                "Order not confirmed",
                "Confirm the order before creating an invoice.",
            )
            return
        if status == "cancelled":
            self.msg_manager.warning(
                "Order cancelled",
                "Cannot create an invoice for a cancelled order.",
            )
            return
        self.open_create_dialog('sales_invoice')

    def confirm_selected(self):
        """Confirm the selected draft sales order."""
        row = self.get_selected_sales_order()
        if not row:
            self.msg_manager.warning(
                "No selection",
                "Select a draft order to confirm.",
            )
            return

        status = (row.get("status") or "").lower()
        if status != "draft":
            self.msg_manager.warning(
                "Not draft",
                f"Only DRAFT orders can be confirmed "
                f"(current status: {row.get('status', '?')}).",
            )
            return

        order_id = row.get("id")
        label = row.get("code") or order_id
        if not self.msg_manager.question(
            "Confirm order",
            f"Confirm order {label}?",
        ):
            return

        self.overlay.show_message("Confirming order...")
        self.executor.run(
            self.controller.confirm_sales_order,
            order_id,
            on_result=self._on_action_result,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def cancel_selected(self):
        """Cancel the selected sales order (draft/confirmed/processing)."""
        row = self.get_selected_sales_order()
        if not row:
            self.msg_manager.warning(
                "No selection",
                "Select an order to cancel.",
            )
            return

        status = (row.get("status") or "").lower()
        if status not in {"draft", "confirmed", "processing"}:
            self.msg_manager.warning(
                "Cannot cancel",
                f"Orders with status '{row.get('status', '?')}' "
                f"cannot be cancelled.",
            )
            return

        order_id = row.get("id")
        label = row.get("code") or order_id
        if not self.msg_manager.question(
            "Cancel order",
            f"Cancel order {label}? This cannot be undone easily.",
        ):
            return

        self.overlay.show_message("Cancelling order...")
        self.executor.run(
            self.controller.cancel_sales_order,
            order_id,
            on_result=self._on_action_result,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def _on_action_result(self, result: APIResult):
        if result.ok:
            signals.statusbar_msg.emit(
                "Order updated successfully.",
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

    # ------------------------------------------------------------------
    # Actions / Helpers / Handlers
    # ------------------------------------------------------------------

    # -- Row selection handlers -------------------
    def on_row_selected(self, row: dict):
        """Handle row selection."""
        self._current_row = row
        self.sales_order_selected.emit(row)

    # -- Page changing handlers -------------------
    def on_page_changed(self, page):
        self._current_page = page

    # -- Action handlers ---------------------------
    def get_selected_sales_order(self) -> dict | None:
        """Get the currently selected sales order."""
        return self.table_view.get_selected_row()

    # -- Action handlers ---------------------------
    def get_row(self, row_index: int) -> dict | None:
        """Get specific row"""
        return self.table_view.get_row(row_index)

    # -- Action handlers ---------------------------
    def get_column(self, column_name: str, unique: bool = False) -> list:
        """Get specific column."""
        return self.table_view.get_column(column_name, unique) or []

    # -- Load Sales Orders -----------------------------
    def _on_sales_orders_loaded(self, result):
        if result.ok:
            sales_orders = result.data.get('data', [])
            paginator = result.data.get('paginator', {})

            self._populate(sales_orders, paginator)
            self.set_filters_options()
            self.handle_result(result)

    def _on_return_data(self, result):
        if result.ok:
            self._returned_data = result.data.get('data', [])

    # -- Load Data to Table ------------------------
    def _populate(self, sales_orders: list[dict], paginator: dict) -> None:
        self.table_view.set_data(sales_orders, paginator)

    # -- Update Filters --------------------------------
    def set_filters_options(self) -> None:
        # Status names
        status_names = {
            status_name: status_name
            for status_name in self.get_column("status", []) if status_name
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
                f"Could not load sales orders: {result.error}",
                TimeOut.TIMEOUT_5000,
                True
            )
