"""
Sales payments management tab.
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
    SALES_PAYMENTS_COLUMN_MAP,
    SALES_PAYMENTS_NAVBAR_COMPONENTS,
)
from frontend.utils.config import DEFAULT_PAGE_SIZE

from frontend.ui.dialogs import ShowDataDialog
from frontend.controllers import SalesController


class SalesPaymentsTab(QWidget):
    """Sales payments list tab."""

    payment_selected = pyqtSignal(dict)
    payment_added = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.controller = SalesController()
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
        self._last_filter = None

        self.setup_ui()
        self.connect_signals()
        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.navbar = Navbar(self)
        self.table_model = GenericTableModel(
            headers=list(SALES_PAYMENTS_COLUMN_MAP.keys()),
            column_map=SALES_PAYMENTS_COLUMN_MAP,
        )
        self.table_view = PaginatedTableView(self.table_model)
        self._configure_navbar()

        layout.addWidget(self.navbar)
        layout.addWidget(self.table_view)

    def _configure_navbar(self):
        # Payments are recorded from the Sales Invoices tab.
        # Refund is available here for completed/partial payments.
        self.navbar.configure_icon_button(
            self.navbar.button_1,
            "refund_sales_payment",
            Icon.CIRCLE_X,
            Color.COLOR_RE02,
            "Refund selected payment",
        )
        self.navbar.set_components_visible(SALES_PAYMENTS_NAVBAR_COMPONENTS)

    def connect_signals(self):
        self.navbar.refresh_clicked.connect(self.refresh)
        self.navbar.button_1_clicked.connect(self.refund_selected)
        self.table_view.row_selected.connect(self.on_row_selected)
        self.table_view.row_double_clicked.connect(self.show_payment_details)
        self.table_view.page_changed.connect(self.on_page_changed)

    def get_all_data(self, model: str):
        self.overlay.show()
        data = self.controller.get_all(model)
        self.overlay.hide()
        return data


    def refresh(self):
        self._current_page = 1
        self._current_row = None
        self.load_data()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.overlay:
            self.overlay.setGeometry(self.rect())

    def load_data(self) -> None:
        self.overlay.show_message("Loading payments...")
        self._last_filter = self.navbar.get_all_filters()
        self.executor.run(
            self.controller.load_sales_payments,
            self._current_page,
            self._page_size,
            self._last_filter.get("search", ""),
            self._last_filter.get("status", "") or None,
            on_result=self._on_payments_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def refund_selected(self):
        """Refund the selected completed/partial payment."""
        row = self.table_view.get_selected_row() or self._current_row
        if not row:
            self.msg_manager.warning(
                "No selection",
                "Select a completed or partial payment to refund.",
            )
            return
        status = (row.get("status") or "").lower()
        if status not in {"completed", "partial"}:
            self.msg_manager.warning(
                "Cannot refund",
                f"Only completed or partial payments can be refunded "
                f"(current status: {row.get('status', '?')}).",
            )
            return
        payment_id = row.get("id")
        amount = row.get("amount", "?")
        if not self.msg_manager.question(
            "Refund payment",
            f"Refund payment of {amount}? "
            f"The invoice balance will be reduced.",
        ):
            return
        self.overlay.show_message("Refunding payment...")
        self.executor.run(
            self.controller.refund_sales_payment,
            payment_id,
            on_result=self._on_refund_result,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def _on_refund_result(self, result: APIResult):
        if result.ok:
            signals.statusbar_msg.emit(
                "Payment refunded successfully.",
                TimeOut.TIMEOUT_5000,
                False,
            )
            self.refresh()
        else:
            self.msg_manager.error(
                "Refund failed",
                str(result.error or "Unknown error"),
            )

    def show_payment_details(self, row: dict):

        self._current_row = row
        self.overlay.show_message("Loading payment details...")
        self.executor.run(
            self.controller.get_sales_payment,
            row["id"],
            on_result=self._on_payment_details_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def _on_payment_details_loaded(self, result):
        if result.ok:
            dialog = ShowDataDialog(
                result.data.get("data", {}),
                SALES_PAYMENTS_COLUMN_MAP,
                None,
                f"Payment {self._current_row.get('id', '')} Details",
            )
            dialog.exec()
        else:
            self.msg_manager.error(
                "Could Not Load Payment",
                f"{result.error}",
            )

    def on_row_selected(self, row: dict):
        self._current_row = row
        self.payment_selected.emit(row)

    def on_page_changed(self, page):
        self._current_page = page
        self.load_data()

    def get_column(self, column_name: str, unique: bool = False) -> list:
        return self.table_view.get_column(column_name, unique) or []

    def _on_payments_loaded(self, result):
        if result.ok:
            payments = result.data.get("data", [])
            paginator = result.data.get("paginator", {})
            self.table_view.set_data(payments, paginator)
            status_names = {
                s: s for s in self.get_column("status", unique=True) if s
            }
            self.navbar.set_status_items({"": "", **status_names})
            self.handle_result(result)

    def _on_worker_error(self, error):
        self.msg_manager.error(
            f"{error.get('type', 'Error')}",
            f"{error.get('message', '')}",
        )

    def _on_worker_finished(self):
        self.overlay.hide()

    def handle_result(self, result: APIResult):
        if result.ok:
            signals.statusbar_msg.emit(
                "Request Success, Data Loaded",
                TimeOut.TIMEOUT_5000,
                False,
            )
        elif result.server_error:
            signals.statusbar_msg.emit(
                "Server unavailable — showing last loaded data.",
                TimeOut.TIMEOUT_5000,
                True,
            )
        else:
            signals.statusbar_msg.emit(
                f"Could not load payments: {result.error}",
                TimeOut.TIMEOUT_5000,
                True,
            )
