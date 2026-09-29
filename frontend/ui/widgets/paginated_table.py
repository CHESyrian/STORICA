from PyQt6.QtWidgets import (
    QComboBox, QHBoxLayout, QHeaderView, QLabel, QPushButton,
    QTableView, QVBoxLayout, QWidget, 
)
from PyQt6.QtCore import Qt, pyqtSignal

from frontend.utils.config import DEFAULT_PAGE_SIZE
from frontend.utils.constants import Color, Icon

from .custom_icons import color_icon


class PaginatedTableView(QWidget):
    """
    Paginated table view that wraps any ``QAbstractTableModel``.

    Signals:
        page_changed(int)        : Emitted with the requested page number.
        page_size_changed(int)   : Emitted when the rows-per-page selector changes.
        row_selected(dict)       : Emitted with the row dict on single click.
        row_double_clicked(dict) : Emitted with the row dict on double-click.
    """

    page_changed = pyqtSignal(int)
    page_size_changed = pyqtSignal(int)
    row_selected = pyqtSignal(dict)
    row_double_clicked = pyqtSignal(dict)

    def __init__(self, model, stretch: bool = True, parent=None) -> None:
        super().__init__(parent)

        self._model = model
        self._stretch = stretch

        # Pagination state
        self._raw_data: list = []
        self._total_count: int = 0
        self._current_page: int = 1
        self._page_size: int = DEFAULT_PAGE_SIZE
        self._total_pages: int = 1

        self._build_ui()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_data(self, data: list, paginator: dict) -> None:
        """
        Populate the table from an API response.

        Args:
            data:      List of row dicts.
            paginator: Dict with keys ``count``, ``page``, ``page_size``,
                       ``total_pages``, ``next``, ``previous``.
        """
        self._raw_data = data
        self._total_count = paginator.get("count", 0)
        self._current_page = paginator.get("page", 1)
        self._page_size = paginator.get("page_size", DEFAULT_PAGE_SIZE)
        self._total_pages = paginator.get("total_pages", 1)

        # GenericTableModel uses set_rows(); keep this consistent
        self._model.set_rows(data)
        self._refresh_pagination_ui()

    def update_model_headers(
        self,
        headers: list | None = None,
        column_map: dict | None = None,
    ) -> None:
        """Update the underlying model's headers and/or column mapping."""
        if headers is not None:
            self._model.set_headers(headers)
            
        if column_map is not None:
            self._model.set_column_map(column_map)

    def refresh(self) -> None:
        """Re-request the current page from the caller."""
        self.page_changed.emit(self._current_page)

    # Read-only properties ---------------------------------------------------

    @property
    def current_page(self) -> int:
        return self._current_page

    @property
    def page_size(self) -> int:
        return self._page_size

    @property
    def total_count(self) -> int:
        return self._total_count

    @property
    def total_pages(self) -> int:
        return self._total_pages

    # Get Data ---------------------------------------------------

    def get_selected_row(self) -> dict | None:
        """Return the currently selected row dict, or ``None``."""
        indexes = self._table.selectedIndexes()
        if indexes:
            return self._row_at(indexes[0].row())
        return None

    def get_row(self, row: int) -> dict | None:
        """
        Return all values from a row by its index.

        Example:
            table.get_row(3)
        """
        if self._raw_data:
            return self._raw_data[row]
        return

    def get_column(self, column_name: str, unique: bool = False) -> list:
        """
        Return all values from a column by its name.

        Example:
            table.get_column("id")
            table.get_column("name")
        """
        if self._raw_data:
            values = [
                row.get(column_name)
                for row in self._raw_data
            ]

            if unique:
                values = list(dict.fromkeys(values))
                
            return values
        return

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._build_table())
        layout.addWidget(self._build_pagination_bar())

    def _build_table(self) -> QTableView:
        self._table = QTableView()
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(
            QTableView.SelectionBehavior.SelectRows
        )
        self._table.setSelectionMode(
            QTableView.SelectionMode.SingleSelection
        )
        self._table.setSortingEnabled(False)
        self._table.setEditTriggers(
            QTableView.EditTrigger.NoEditTriggers
        )
        self._table.verticalHeader().setVisible(False)
        self._table.setModel(self._model)

        header = self._table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
        header.setStretchLastSection(self._stretch)

        self._table.clicked.connect(self._on_row_clicked)
        self._table.doubleClicked.connect(self._on_row_double_clicked)

        return self._table

    def _build_pagination_bar(self) -> QWidget:
        bar = QWidget()
        bar.setObjectName('paginatorBar')
        
        layout = QHBoxLayout(bar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Navigation buttons ---------------------------------------
        self._first_btn = self._nav_button(
            self._go_first, 
            Icon.CHEVRONS_LEFT, 
            Color.COLOR_BU03
        )
        self._prev_btn = self._nav_button(
            self._go_prev, 
            Icon.CHEVRON_LEFT, 
            Color.COLOR_BU03
        )
        self._page_label = QLabel()
        self._page_label.setMinimumWidth(110)
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._next_btn = self._nav_button(
            self._go_next, 
            Icon.CHEVRON_RIGHT, 
            Color.COLOR_BU03
        )
        self._last_btn = self._nav_button(
            self._go_last, 
            Icon.CHEVRONS_RIGHT, 
            Color.COLOR_BU03
        )

        # Summary label ---------------------------------------
        self._info_label = QLabel()
        self._info_label.setMinimumWidth(150)

        # Layouts --------------------------------------------
        layout.addStretch()
        for widget in (
            self._first_btn,
            self._prev_btn,
            self._page_label,
            self._next_btn,
            self._last_btn,
        ):
            layout.addWidget(widget)

        layout.addStretch()
        layout.addWidget(self._info_label)

        return bar

    @staticmethod
    def _nav_button(slot, icon_path: str=None, icon_color: str=None) -> QPushButton:
        btn = QPushButton()
        btn.setFixedSize(30, 30)
        btn.setIcon(color_icon(icon_path, icon_color))
        btn.setObjectName('paginatorBtn')
        btn.clicked.connect(slot)
        return btn

    # ------------------------------------------------------------------
    # Pagination actions
    # ------------------------------------------------------------------

    def _go_first(self) -> None:
        if self._current_page != 1:
            self.page_changed.emit(1)

    def _go_prev(self) -> None:
        if self._current_page > 1:
            self.page_changed.emit(self._current_page - 1)

    def _go_next(self) -> None:
        if self._current_page < self._total_pages:
            self.page_changed.emit(self._current_page + 1)

    def _go_last(self) -> None:
        if self._current_page != self._total_pages:
            self.page_changed.emit(self._total_pages)

    # ------------------------------------------------------------------
    # Row-click handlers
    # ------------------------------------------------------------------

    def _on_row_clicked(self, index) -> None:
        row = self._row_at(index.row())
        if row is not None:
            self.row_selected.emit(row)

    def _on_row_double_clicked(self, index) -> None:
        row = self._row_at(index.row())
        if row is not None:
            self.row_double_clicked.emit(row)

    def _row_at(self, row: int) -> dict | None:
        if 0 <= row < len(self._raw_data):
            return self._raw_data[row]
        return None

    # ------------------------------------------------------------------
    # UI state refresh
    # ------------------------------------------------------------------

    def _refresh_pagination_ui(self) -> None:
        self._page_label.setText(
            f"Page {self._current_page} of {self._total_pages}"
        )

        has_prev = self._current_page > 1
        has_next = self._current_page < self._total_pages
        self._first_btn.setEnabled(has_prev)
        self._prev_btn.setEnabled(has_prev)
        self._next_btn.setEnabled(has_next)
        self._last_btn.setEnabled(has_next)

        if self._total_count > 0:
            start = (self._current_page - 1) * self._page_size + 1
            end = min(self._current_page * self._page_size, self._total_count)
            self._info_label.setText(
                f"{start} – {end} of {self._total_count}"
            )
        else:
            self._info_label.setText("No items")


