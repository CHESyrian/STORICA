from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtGui import QColor

from frontend.utils.constants import (
    PAYMENT_COLOURS,
    STATUS_COLOURS,
    BOOLEAN_COLOURS,
    LOW_STOCK_COLOURS,
    STATUS_TOOLTIPS,
    NUMERIC_FIELDS,
)


class GenericTableModel(QAbstractTableModel):
    """
    Qt model for tabular data with header mapping and colour coding.

    Args:
        headers:    Ordered list of display column names shown to the user.
        column_map: Mapping of display header → data field name.
                    Example: {"Product Name": "product_name", "Price": "price"}
        parent:     Optional Qt parent object.
    """

    def __init__(
        self,
        headers: Optional[List[str]] = None,
        column_map: Optional[Dict[str, str]] = None,
        parent=None,
    ) -> None:
        super().__init__(parent)

        self._headers: List[str] = headers or []
        self._column_map: Dict[str, str] = column_map or {}
        self._data: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public data-management API
    # ------------------------------------------------------------------

    def set_rows(self, rows: List[Dict[str, Any]]) -> None:
        """Replace the entire dataset with *rows*."""
        self.beginResetModel()
        self._data = list(rows)
        self.endResetModel()

    def append_rows(self, rows: List[Dict[str, Any]]) -> None:
        """Append *rows* to the existing dataset."""
        if not rows:
            return
        first = len(self._data)
        last = first + len(rows) - 1
        self.beginInsertRows(QModelIndex(), first, last)
        self._data.extend(rows)
        self.endInsertRows()

    def update_row(self, row: int, row_data: Dict[str, Any]) -> None:
        """Merge *row_data* into the existing record at *row*."""
        if 0 <= row < len(self._data):
            self._data[row].update(row_data)
            left = self.index(row, 0)
            right = self.index(row, self.columnCount() - 1)
            self.dataChanged.emit(left, right)

    def remove_row(self, row: int) -> None:
        """Delete the record at *row*."""
        if 0 <= row < len(self._data):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self._data[row]
            self.endRemoveRows()

    def clear(self) -> None:
        """Remove all rows."""
        self.beginResetModel()
        self._data = []
        self.endResetModel()

    # ------------------------------------------------------------------
    # Header configuration
    # ------------------------------------------------------------------

    def set_headers(self, headers: List[str]) -> None:
        """Replace column headers (triggers full model reset)."""
        self.beginResetModel()
        self._headers = list(headers)
        self.endResetModel()

    def set_column_map(self, column_map: Dict[str, str]) -> None:
        """Replace the display-header → field-name mapping."""
        self.beginResetModel()
        self._column_map = dict(column_map)
        self.endResetModel()

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def get_row(self, row: int) -> Optional[Dict[str, Any]]:
        """Return a copy of the row dict at *row*, or ``None``."""
        if 0 <= row < len(self._data):
            return dict(self._data[row])
        return None

    def get_column(self, column_name: str) -> list:
        key = self.column_map.get(column_name, column_name)

        return [
            row.get(key)
            for row in self._data
        ]

    def get_all_data(self) -> List[Dict[str, Any]]:
        """Return a shallow copy of the full dataset."""
        return list(self._data)

    # ------------------------------------------------------------------
    # QAbstractTableModel interface
    # ------------------------------------------------------------------

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._headers)

    def headerData(  # noqa: N802
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Optional[str]:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
            and section < len(self._headers)
        ):
            return self._headers[section]
        return None

    def data(
        self,
        index: QModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if not index.isValid() or index.row() >= len(self._data):
            return None

        row_dict = self._data[index.row()]
        field = self._field_name(index.column())
        value = row_dict.get(field)

        if role == Qt.ItemDataRole.DisplayRole:
            return "" if value is None else str(value)

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return self._alignment(field)

        if role == Qt.ItemDataRole.ForegroundRole:
            return self._foreground(field, row_dict)

        if role == Qt.ItemDataRole.BackgroundRole:
            return self._background(row_dict)

        if role == Qt.ItemDataRole.ToolTipRole:
            return self._tooltip(field, row_dict)

        return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _field_name(self, column: int) -> str:
        """Resolve the data-dict key for *column*."""
        if column >= len(self._headers):
            return ""
        header = self._headers[column]
        return self._column_map.get(header, header.lower().replace(" ", "_"))

    @staticmethod
    def _alignment(field: str) -> Qt.AlignmentFlag:
        is_numeric = field in NUMERIC_FIELDS or any(
            tok in field for tok in NUMERIC_FIELDS
        )
        h = (
            Qt.AlignmentFlag.AlignRight
            if is_numeric
            else Qt.AlignmentFlag.AlignLeft
        )
        return h | Qt.AlignmentFlag.AlignVCenter

    @staticmethod
    def _is_low_stock_row(row: Dict[str, Any]) -> bool:
        val = row.get("is_low_stock")
        if isinstance(val, bool):
            return val
        if val is None:
            return False
        return str(val).lower() in ("true", "1", "yes")

    @staticmethod
    def _foreground(field: str, row: Dict[str, Any]) -> Optional[QColor]:
        if field == "payment":
            entry = PAYMENT_COLOURS.get(row.get("payment", "").lower())
            return entry["fg"] if entry else None

        if field == "status":
            return STATUS_COLOURS.get(row.get("status", "").lower())

        if field == "is_verified":
            return BOOLEAN_COLOURS.get(str(row.get("is_verified", "")))

        if field == "is_active":
            return BOOLEAN_COLOURS.get(str(row.get("is_active", "")))

        if field == "is_low_stock":
            if GenericTableModel._is_low_stock_row(row):
                return LOW_STOCK_COLOURS["fg"]
            return BOOLEAN_COLOURS.get("False")

        if GenericTableModel._is_low_stock_row(row):
            return LOW_STOCK_COLOURS["fg"]

        return None

    @staticmethod
    def _background(row: Dict[str, Any]) -> Optional[QColor]:
        if GenericTableModel._is_low_stock_row(row):
            return LOW_STOCK_COLOURS["bg"]

        entry = PAYMENT_COLOURS.get(str(row.get("payment", "")).lower())
        return entry["bg"] if entry else None

    @staticmethod
    def _tooltip(field: str, row: Dict[str, Any]) -> Optional[str]:
        if field == "status":
            return STATUS_TOOLTIPS.get(row.get("status", ""), "")

        if GenericTableModel._is_low_stock_row(row):
            qty = row.get("quantity", "?")
            min_stock = row.get("min_stock", "?")
            return f"Low stock: on-hand {qty} ≤ min {min_stock}"

        return None

