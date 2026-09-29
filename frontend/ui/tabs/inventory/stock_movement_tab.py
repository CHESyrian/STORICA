"""
Stock movements tab for inventory management.
Includes navbar and paginated table for stock movement management.
Supports create (PENDING) and complete (PENDING → COMPLETED).
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
from frontend.utils.constants import (
    Color, Icon,
    STOCK_MOVEMENTS_COLUMN_MAP,
    STOCK_MOVEMENTS_NAVBAR_COMPONENTS,
)
from frontend.utils.config import DEFAULT_PAGE_SIZE
from frontend.utils.dialog_handler import DialogHandler
from frontend.controllers import StockMovementController
from frontend.ui.dialogs import AddStockMovementDialog


class StockMovementTab(QWidget):
    """
    Stock movements management tab.
    Fixed tab that cannot be closed or removed.
    Create PENDING movements and complete them to apply stock changes.
    """

    movement_selected = pyqtSignal(dict)
    movement_added = pyqtSignal(dict)
    movement_completed = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.controller = StockMovementController()
        self.msg_manager = MessageManager()
        self.executor = AsyncExecutor()
        self.overlay = LoadingOverlay(self)
        self.dialog_handler = DialogHandler(
            executor=self.executor,
            overlay=self.overlay,
            message_manager=self.msg_manager,
        )
        self._current_page = None
        self._page_size = DEFAULT_PAGE_SIZE
        self._current_row = None
        self._last_filters = None

        self.setup_ui()
        self.connect_signals()

        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        """Setup the stock movements tab UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.navbar = Navbar(self)

        self.table_model = GenericTableModel(
            headers=list(STOCK_MOVEMENTS_COLUMN_MAP.keys()),
            column_map=STOCK_MOVEMENTS_COLUMN_MAP,
        )
        self.table_view = PaginatedTableView(self.table_model)

        self._configure_navbar()

        layout.addWidget(self.navbar)
        layout.addWidget(self.table_view)

    def _configure_navbar(self):
        """Configure the navbar controls.
        Complete only — movements are created by sales/purchases flows.
        """
        self.navbar.configure_icon_button(
            self.navbar.button_2,
            "complete_movement",
            Icon.SEND,
            Color.COLOR_BU06,
            "Complete selected pending movement",
        )
        self.navbar.set_components_visible(STOCK_MOVEMENTS_NAVBAR_COMPONENTS)

    def connect_signals(self):
        """Connect all signals."""
        self.navbar.refresh_clicked.connect(self.refresh)
        # Manual add removed — movements are created by sales/purchases
        self.navbar.button_2_clicked.connect(self.complete_selected)

        self.table_view.row_selected.connect(self.on_row_selected)
        self.table_view.page_changed.connect(self.on_page_changed)

    def get_all_data(self, model: str):
        self.overlay.show()
        data = self.controller.get_all(model)
        self.overlay.hide()
        return data

    def add_dialog(self):
        """Open the add stock-movement dialog with lookup options."""
        dialog = AddStockMovementDialog()

        products = self.get_all_data("products")
        batches = self.get_all_data("batches")
        warehouses = self.get_all_data("warehouses")

        if products.ok:
            opts = {
                f"{p.get('sku', '')} — {p.get('name', '')}": p["id"]
                for p in products.data.get("data", [])
                if p.get("id")
            }
            dialog.set_product_options(opts)
        if batches.ok:
            opts = {
                f"{b.get('code', '')} ({b.get('variant_sku', '')})": b["id"]
                for b in batches.data.get("data", [])
                if b.get("id")
            }
            dialog.set_batch_options(opts)
        if warehouses.ok:
            opts = {
                f"{w.get('code', '')} — {w.get('name', '')}": w["id"]
                for w in warehouses.data.get("data", [])
                if w.get("id")
            }
            dialog.set_warehouse_options(opts)

        self.dialog_handler.open(
            dialog=dialog,
            create_fn=self.controller.create_stock_movement,
            entity_name="Stock Movement",
        )
        # Reload list after dialog closes (create may have succeeded)
        self.refresh()

    def complete_selected(self):
        """Complete the selected PENDING movement (applies stock changes)."""
        row = self.get_selected_movement()
        if not row:
            self.msg_manager.warning(
                "No selection",
                "Select a pending stock movement to complete.",
            )
            return

        status = (row.get("status") or "").lower()
        if status != "pending":
            self.msg_manager.warning(
                "Not pending",
                f"Only PENDING movements can be completed "
                f"(current status: {row.get('status', '?')}).",
            )
            return

        movement_id = row.get("id")
        if not movement_id:
            self.msg_manager.error("Invalid row", "Selected movement has no id.")
            return

        label = (
            f"{row.get('movement_id') or movement_id} — "
            f"{row.get('movement_type', '')} "
            f"{row.get('product_name', '')} "
            f"qty {row.get('quantity', '')}"
        )
        confirmed = self.msg_manager.question(
            "Complete movement",
            f"Complete this stock movement?\n\n{label}",
            "Stock quantities will be updated. This cannot be undone.",
            parent=self,
        )
        if not confirmed:
            return

        self.overlay.show_message("Completing stock movement...")
        self.executor.run(
            self.controller.partial_update_stock_movement,
            movement_id,
            {"status": "completed"},
            on_result=self._on_complete_result,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def _on_complete_result(self, result: APIResult):
        if result.ok:
            data = result.data.get("data") if isinstance(result.data, dict) else result.data
            if isinstance(data, dict):
                self.movement_completed.emit(data)
            signals.statusbar_msg.emit(
                "Stock movement completed — quantities updated.",
                4000,
                False,
            )
            self.refresh()
        else:
            self.msg_manager.error(
                "Complete failed",
                str(result.error or result.data or "Unknown error"),
            )

    def refresh(self):
        """Refresh the current page data."""
        self._current_page = 1
        self.load_data()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.overlay:
            self.overlay.setGeometry(self.rect())

    def load_data(self) -> None:
        self.overlay.show_message("Loading stock movements...")
        self._last_filters = self.navbar.get_all_filters()

        search = self._last_filters.get("search")
        status = self._last_filters.get("status") or None
        choice = self._last_filters.get("choice") or None

        self.executor.run(
            self.controller.load_stock_movements,
            self._current_page,
            self._page_size,
            search,
            choice,  # movement_type via choice dropdown
            status,
            on_result=self._on_movements_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def _populate(self, movements: list[dict], paginator: dict) -> None:
        self.table_view.set_data(movements, paginator)

    def set_filters_options(self) -> None:
        status_values = self.get_column("status", unique=True)
        status_options = {
            s: s.replace("_", " ").title() for s in status_values if s
        }
        self.navbar.set_status_items({"": "", **status_options})

        movement_types = self.get_column("movement_type", unique=True)
        self.navbar.set_choice_items([""] + [t for t in movement_types if t])

    def on_row_selected(self, row: dict):
        self._current_row = row
        self.movement_selected.emit(row)

    def on_page_changed(self, page):
        self._current_page = page
        self.load_data()

    def get_selected_movement(self) -> dict | None:
        return self.table_view.get_selected_row()

    def get_row(self, row_index: int) -> dict | None:
        return self.table_view.get_row(row_index)

    def get_column(self, column_name: str, unique: bool = False) -> list:
        return self.table_view.get_column(column_name, unique) or []

    def _on_movements_loaded(self, result):
        if result.ok:
            movements = result.data.get("data", [])
            paginator = result.data.get("paginator", {})
            self._populate(movements, paginator)
            self.set_filters_options()
            self.handle_result(result)

    def _on_worker_error(self, error):
        self.msg_manager.error(
            f"{error.get('type', 'Error')}",
            f"{error.get('message', '')} \n {error.get('traceback', '')}",
        )

    def _on_worker_finished(self):
        self.overlay.hide()

    def handle_result(self, result: APIResult):
        if result.ok:
            signals.statusbar_msg.emit(
                "Request Success, Data Loaded",
                3000,
                False,
            )
        elif result.server_error:
            signals.statusbar_msg.emit(
                "Server unavailable — showing last loaded data.",
                3000,
                True,
            )
        elif result.not_found:
            signals.statusbar_msg.emit(
                "No data found.",
                3000,
                False,
            )
        else:
            signals.statusbar_msg.emit(
                f"Could not load stock movements: {result.error}",
                3000,
                True,
            )
