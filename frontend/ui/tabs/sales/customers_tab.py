"""
Customers tab for sales management.
Includes navbar and paginated table for customer management.
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
    CUSTOMERS_COLUMN_MAP, 
    CUSTOMERS_NAVBAR_COMPONENTS, 
)
from frontend.utils.config import DEFAULT_PAGE_SIZE

from frontend.controllers import CustomerController

from frontend.ui.dialogs import (
    AddCustomerDialog
)


class CustomersTab(QWidget):
    """
    Customers management tab.
    Fixed tab that cannot be closed or removed.
    """

    customer_selected = pyqtSignal(dict)
    customer_added    = pyqtSignal(dict)
    customer_updated  = pyqtSignal(dict)
    customer_deleted  = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.controller     = CustomerController()
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
            "customer": (
                AddCustomerDialog,
                lambda self: (),
                self.controller.create_customer,
                "Customer",
            )
        }

        self.setup_ui()
        self.connect_signals()

        # Set toast parent for this widget
        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        """Setup the customers tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create navbar
        self.navbar = Navbar(self)

        # Create table model and view
        self.table_model = GenericTableModel(
            headers=list(CUSTOMERS_COLUMN_MAP.keys()),
            column_map=CUSTOMERS_COLUMN_MAP
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
            "add_customer",
            Icon.FILE_PLUS_CORNER,
            Color.COLOR_GR02,
            "Add new customer"
        )

        self.navbar.configure_icon_button(
            self.navbar.button_2,
            "edit_customer",
            Icon.FILE_PEN_LINE,
            Color.COLOR_PU02,
            "Edit selected customer"
        )

        self.navbar.configure_icon_button(
            self.navbar.button_3,
            "delete_customer",
            Icon.TRASH_2,
            Color.COLOR_RE02,
            "Delete selected customer"
        )

        self.navbar.configure_icon_button(
            self.navbar.button_4,
            "view_customer_orders",
            Icon.SHOPPING_CART,
            Color.COLOR_YE02,
            "View customer orders"
        )
        self.navbar.configure_flag(
            "Verified only",
            tooltip="Show only verified customers",
            checked=False,
        )
        self.navbar.set_components_visible(CUSTOMERS_NAVBAR_COMPONENTS)

    def connect_signals(self):
        """Connect all signals."""
        # Navbar signals
        self.navbar.refresh_clicked.connect(self.refresh)
        self.navbar.button_1_clicked.connect(self.add_dialog)
        self.navbar.button_2_clicked.connect(self.edit_customer)
        self.navbar.button_3_clicked.connect(self.delete_customer)
        self.navbar.button_4_clicked.connect(self.view_customer_orders)
        self.navbar.flag_changed.connect(lambda _=None: self.refresh())
        self.navbar.active_changed.connect(lambda _=None: self.refresh())

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

        self.overlay.show_message("Loading customers...")

        self._last_filter = self.navbar.get_all_filters()

        verified = True if self._last_filter.get("flag") else None
        self.executor.run(
            self.controller.load_customers,
            self._current_page,
            self._page_size,
            self._last_filter.get("search"),
            self._last_filter.get("active"),
            verified,
            on_result=self._on_customers_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    # -- Dialogs -------------------------------------
    def add_dialog(self):
        """Open the add customer dialog."""
        self.open_create_dialog('customer')

    def edit_customer(self):
        """Edit the selected customer."""
        selected_row = self.get_selected_customer()
        if not selected_row:
            self.msg_manager.warning(
                "No Selection",
                "Please select a customer to edit."
            )
            return
        
        # Open edit dialog with selected customer data
        self.msg_manager.info(
            "Edit Customer",
            f"Editing customer: {selected_row.get('name', '')}"
        )

    def delete_customer(self):
        """Delete the selected customer."""
        selected_row = self.get_selected_customer()
        if not selected_row:
            self.msg_manager.warning(
                "No Selection",
                "Please select a customer to delete."
            )
            return
        
        # Confirm deletion
        self.msg_manager.info(
            "Delete Customer",
            f"Deleting customer: {selected_row.get('name', '')}"
        )

    def view_customer_orders(self):
        """View orders for the selected customer."""
        selected_row = self.get_selected_customer()
        if not selected_row:
            self.msg_manager.warning(
                "No Selection",
                "Please select a customer to view orders."
            )
            return
        
        # Navigate to orders tab with customer filter
        self.msg_manager.info(
            "View Orders",
            f"Viewing orders for customer: {selected_row.get('name', '')}"
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
        self.customer_selected.emit(row)

    # -- Page changing handlers -------------------
    def on_page_changed(self, page):
        self._current_page = page

    # -- Action handlers ---------------------------
    def get_selected_customer(self) -> dict | None:
        """Get the currently selected customer."""
        return self.table_view.get_selected_row()

    # -- Action handlers ---------------------------
    def get_row(self, row_index: int) -> dict | None:
        """Get specific row"""
        return self.table_view.get_row(row_index)

    # -- Action handlers ---------------------------
    def get_column(self, column_name: str, unique: bool = False) -> list:
        """Get specific column."""
        return self.table_view.get_column(column_name, unique) or []

    # -- Load Customers -----------------------------
    def _on_customers_loaded(self, result):
        if result.ok:
            customers = result.data.get('data', [])
            paginator = result.data.get('paginator', {})

            self._populate(customers, paginator)
            self.set_filters_options()
            self.handle_result(result)

    # -- Load Data to Table ------------------------
    def _populate(self, customers: list[dict], paginator: dict) -> None:
        self.table_view.set_data(customers, paginator)

    # -- Update Filters --------------------------------
    def set_filters_options(self) -> None:
        # Customer types/segments
        customer_types = self.get_column("type", unique=True)
        customer_types = [t for t in customer_types if t]  # Remove empty values
        
        type_options = {t: t for t in customer_types}
        self.navbar.set_choice_items({"": "", **type_options})

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
                f"Could not load customers: {result.error}",
                TimeOut.TIMEOUT_5000,
                True
            )