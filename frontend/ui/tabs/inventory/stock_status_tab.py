"""
Stock status tab for inventory management.
Read-only view of on-hand stock by variant × warehouse.
Low-stock rows are colour-highlighted; navbar flag is labeled
"Low stock only" for this tab only.
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
    STOCK_STATUS_COLUMN_MAP,
    STOCK_STATUS_NAVBAR_COMPONENTS,
)
from frontend.utils.config import DEFAULT_PAGE_SIZE
from frontend.controllers import StockStatusController


class StockStatusTab(QWidget):
    """
    Stock status (read-only) tab.
    Shows current stock levels per variant/warehouse.
    """

    status_selected = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        self.controller = StockStatusController()
        self.msg_manager = MessageManager()
        self.executor = AsyncExecutor()
        self.overlay = LoadingOverlay(self)
        self._current_page = None
        self._page_size = DEFAULT_PAGE_SIZE
        self._current_row = None
        self._last_filters = None
        self._loading = False

        self.setup_ui()
        self.connect_signals()

        self.msg_manager.set_toast_parent(self)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.navbar = Navbar(self)

        self.table_model = GenericTableModel(
            headers=list(STOCK_STATUS_COLUMN_MAP.keys()),
            column_map=STOCK_STATUS_COLUMN_MAP,
        )
        self.table_view = PaginatedTableView(self.table_model)

        self._configure_navbar()

        layout.addWidget(self.navbar)
        layout.addWidget(self.table_view)

    def _configure_navbar(self):
        """Stock-status private: reuse generic flag as Low stock only."""
        self.navbar.configure_flag(
            "Low stock only",
            tooltip="Show only variants at or below their min stock level",
            checked=False,
        )
        self.navbar.set_components_visible(STOCK_STATUS_NAVBAR_COMPONENTS)

    def connect_signals(self):
        self.navbar.refresh_clicked.connect(self.refresh)
        self.navbar.flag_changed.connect(self._on_flag_toggled)
        self.navbar.status_changed.connect(lambda _=None: self.refresh())
        self.navbar.choice_changed.connect(lambda _=None: self.refresh())
        self.navbar.search_changed.connect(self._on_search_changed)

        self.table_view.row_selected.connect(self.on_row_selected)
        self.table_view.page_changed.connect(self.on_page_changed)

    def _on_flag_toggled(self, _checked: bool) -> None:
        self.refresh()

    def _on_search_changed(self, _text: str) -> None:
        pass

    def refresh(self):
        self._current_page = 1
        self.load_data()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.overlay:
            self.overlay.setGeometry(self.rect())

    def load_data(self) -> None:
        # Guard against re-entrant refresh while a request is in flight
        # (e.g. filter combo rebuild used to re-emit status_changed).
        if self._loading:
            return
        self._loading = True

        self.overlay.show_message("Loading stock status...")
        self._last_filters = self.navbar.get_all_filters()

        search = self._last_filters.get("search") or None
        if search == "":
            search = None

        # Map reusable navbar flag → stock-status low_stock API param
        low_stock_only = bool(self._last_filters.get("flag"))

        self.executor.run(
            self.controller.load_stock_status,
            self._current_page,
            self._page_size,
            search,
            self._last_filters.get("status"),
            self._last_filters.get("choice"),
            None,  # is_active
            low_stock_only,
            on_result=self._on_status_loaded,
            on_error=self._on_worker_error,
            on_finished=self._on_worker_finished,
        )

    def _populate(self, statuses: list[dict], paginator: dict) -> None:
        self.table_view.set_data(statuses, paginator)

    def set_filters_options(self) -> None:
        """
        Rebuild warehouse / category filter lists from the loaded page.

        Must not emit status_changed / choice_changed (those trigger refresh
        and would loop). Navbar setters already blockSignals; restore the
        previous warehouse selection the same way.
        """
        warehouse_names = self.get_column("warehouse_name", True)
        warehouse_ids = self.get_column("warehouse", True)
        warehouses = {
            warehouse_id: warehouse_name
            for warehouse_id, warehouse_name in zip(
                warehouse_ids, warehouse_names
            )
            if warehouse_id and warehouse_name
        }
        current = self.navbar.get_status_filter()
        self.navbar.set_status_items({"": "All warehouses", **warehouses})
        if current not in (None, ""):
            idx = self.navbar.status.findData(current)
            if idx >= 0:
                self.navbar.status.blockSignals(True)
                try:
                    self.navbar.status.setCurrentIndex(idx)
                finally:
                    self.navbar.status.blockSignals(False)

        category_names = self.get_column("category_name", True)
        self.navbar.set_choice_items(
            [""] + [c for c in category_names if c]
        )

    def on_row_selected(self, row: dict):
        self._current_row = row
        self.status_selected.emit(row)

    def on_page_changed(self, page):
        self._current_page = page
        self.load_data()

    def get_selected_status(self) -> dict | None:
        return self.table_view.get_selected_row()

    def get_row(self, row_index: int) -> dict | None:
        return self.table_view.get_row(row_index)

    def get_column(self, column_name: str, unique: bool = False) -> list:
        return self.table_view.get_column(column_name, unique) or []

    def _on_status_loaded(self, result):
        if result.ok:
            statuses = result.data.get("data", [])
            paginator = result.data.get("paginator", {})
            self._populate(statuses, paginator)
            self.set_filters_options()
            self.handle_result(result)

    def _on_worker_error(self, error):
        self.msg_manager.error(
            f"{error.get('type', 'Error')}",
            f"{error.get('message', '')} \n {error.get('traceback', '')}",
        )

    def _on_worker_finished(self):
        self._loading = False
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
                f"Could not load stock status: {result.error}",
                3000,
                True,
            )
