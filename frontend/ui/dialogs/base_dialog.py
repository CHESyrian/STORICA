"""
ui/dialogs/base_dialog.py

Shared scaffolding for the "Add X" and "View X" dialogs.

BaseFormDialog owns the boilerplate every editable dialog repeated:
- fixed-width QDialog with a titled window
- a QVBoxLayout wrapping a QFormLayout + a Save button
- the "generatable field" pattern (a QLineEdit with a trailing
  regenerate action, used by SKU / variant code fields)

BaseDetailDialog builds on that same scaffolding for read-only "View X"
dialogs: subclasses declare a FIELDS map ({label: key} into the raw API
payload dict) and get disabled QLabel rows for free, plus a helper for
rendering nested line-item lists as a read-only table.

Subclasses of BaseFormDialog build their own fields, add them as rows,
call finalize(), and implement get_data(). Subclasses of
BaseDetailDialog just declare FIELDS (and optionally call
add_items_table() from build_ui()).
"""

from __future__ import annotations

import uuid
from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QFormLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QFrame, QTableWidgetItem, QScrollArea, QWidget,
)
from PyQt6.QtGui import QAction

from frontend.ui.widgets import color_icon, StandardTable

from frontend.utils.constants import (
    Color, Icon,
)


REGENERATE_ICON = Icon.REFRESH_CCW_DOT
REGENERATE_ICON_COLOR = Color.COLOR_GR02


class BaseFormDialog(QDialog):
    """Common layout + helpers for single-form "Add X" dialogs."""

    def __init__(self, title: str, width: int = 700):
        super().__init__()

        self.setWindowTitle(title)
        self.setFixedWidth(width)

        self._layout = QVBoxLayout()
        self._layout.setSpacing(20)

        self.form = QFormLayout()
        self.form.setContentsMargins(10, 10, 10, 10)

        self.save_btn = QPushButton("Save")

    # ------------------------------------------------------------------
    # Layout helpers
    # ------------------------------------------------------------------

    def add_row(self, label: str, widget) -> None:
        """Add a labeled field to the form."""
        self.form.addRow(label, widget)

    def add_separator(self) -> None:
        """
        Add a horizontal separator line between sections.
        Creates a QFrame with HLine shape and adds it to the form layout.
        """
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName('separator')

        # Add the separator to the form layout, spanning both columns
        # Use a dummy QLabel as the label and the separator as the field
        self.form.addRow(separator)

    def finalize(self) -> None:
        """
        Assemble the form + save button into the dialog's layout.
        Call this once, at the end of build_ui().
        """
        self._layout.addLayout(self.form)
        self._layout.addWidget(self.save_btn)
        self.setLayout(self._layout)

    # ------------------------------------------------------------------
    # Generatable field helper (SKU / code fields)
    # ------------------------------------------------------------------

    def make_regenerable(
        self,
        line_edit: QLineEdit,
        generator: Callable[[str], str],
        icon_path: str = REGENERATE_ICON,
        icon_color: str = REGENERATE_ICON_COLOR,
    ) -> QAction:
        """
        Attach a trailing "regenerate" action to a QLineEdit.

        `generator` receives only the text the user actually typed
        (never the previously generated value), so clicking regenerate
        repeatedly replaces the suffix instead of stacking a new one
        onto the last generated string each time.
        """
        line_edit._typed_base = ""  # type: ignore[attr-defined]

        def _track_typed_text(text: str) -> None:
            line_edit._typed_base = text  # type: ignore[attr-defined]

        # textEdited only fires on user keystrokes, not on the
        # programmatic setText() below — that's what prevents the
        # generated value from feeding back into itself.
        line_edit.textEdited.connect(_track_typed_text)

        icon = color_icon(icon_path, icon_color)
        action = QAction(icon, "", line_edit)
        action.triggered.connect(
            lambda: line_edit.setText(generator(line_edit._typed_base))  # type: ignore[attr-defined]
        )
        line_edit.addAction(action, QLineEdit.ActionPosition.TrailingPosition)

        return action

    @staticmethod
    def short_uuid(*lengths: int) -> tuple[str, ...]:
        """
        Return one or more slices of a fresh uppercase UUID hex string,
        e.g. short_uuid(5, 5) -> ('A1B2C', '3D4E5').
        """
        raw = uuid.uuid4().hex.upper()
        slices = []
        start = 0
        for length in lengths:
            slices.append(raw[start:start + length])
            start += length
        return tuple(slices)

    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    def get_data(self) -> dict:
        """Return the form's current values as a dict. Override me."""
        raise NotImplementedError


class BaseDetailDialog(BaseFormDialog):
    """
    Read-only "View X" dialog.

    Takes a `fields_map` (required) and an optional `items_map` to render
    a nested list payload as a table. Each mapping follows the same
    {label: key} convention as the *_COLUMN_MAP dicts in constants.py,
    so the detail dialog's field list reads the same as its table's column
    list. Each field renders as a QLabel row (selectable, not editable).

    If `items_map` is provided and `data` contains a non‑empty "items" list,
    the table is added automatically after the main fields.

    There's nothing to save here, so the dialog wires its own button
    (relabeled "Close") straight to accept() — no controller hookup needed.
    """

    def __init__(
        self,
        title: str,
        data: dict,
        width: int = 700,
        fields_map: dict[str, str] | None = None,
        items_map: dict[str, str] | None = None,
    ):
        """
        Args:
            title: Dialog window title.
            data: Raw API payload dictionary.
            width: Dialog width in pixels.
            fields_map: {label: key} mapping for the top‑level fields.
            items_map: {label: key} mapping for nested line items (optional).
        """
        super().__init__(title, width)
        self._data = data or {}
        self._fields_map = fields_map or {}
        self._items_map = items_map
        self.build_ui()

    def build_ui(self) -> None:
        """Render main fields and, if applicable, the items table."""
        # 1. Main fields
        for label, key in self._fields_map.items():
            self.add_row(label, self._make_field(key))

        # 2. Optional nested items table
        if self._items_map:
            items = self._data.get("items")
            if items:   # non‑empty list
                self.add_items_table("Items", items, self._items_map)

        # 3. Finalize (scroll area + Close button)
        self.finalize_readonly()

    # ------------------------------------------------------------------
    # Field rendering
    # ------------------------------------------------------------------

    def _make_field(self, key: str) -> QLabel:
        value = self._data.get(key)
        label = QLabel(self._format_value(key, value))
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setWordWrap(True)

        if key == "status" and value:
            self._style_status(label, str(value))

        return label

    def add_items_table(
        self, label: str, items: list[dict], column_map: dict[str, str]
    ) -> StandardTable:
        """
        Render a nested list payload (order/invoice line items) as a
        read-only table row instead of a single-line field.
        `column_map` follows the same {label: key} convention as fields_map.
        """
        headers = list(column_map.keys())
        keys = list(column_map.values())

        table = StandardTable(headers, stretch=True)
        table.setSortingEnabled(False)   # preserve source order
        table.setRowCount(len(items))

        for row, item in enumerate(items):
            for col, key in enumerate(keys):
                cell = QTableWidgetItem(self._format_value(key, item.get(key)))
                cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, col, cell)

        table.resizeRowsToContents()
        table.setMinimumHeight(min(220, 50 + 45 * max(len(items), 1)))
        table.setMaximumHeight(300)

        self.add_row(label, table)
        
        return table

    def finalize_readonly(self) -> None:
        """
        Wrap the form in a scroll area, swap the inherited Save button
        for a Close button, and cap the dialog's height to keep it sane.
        """
        content = QWidget()
        content.setLayout(self.form)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(content)

        self.save_btn.setText("Close")
        self.save_btn.clicked.connect(self.accept)

        self._layout.addWidget(scroll_area)
        self._layout.addWidget(self.save_btn)
        self.setLayout(self._layout)

        # Fixed max height (no class variable)
        self.setMaximumHeight(600)

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def _format_value(self, key: str, value) -> str:
        if value is None or value == "":
            return "—"

        if isinstance(value, bool):
            return "Yes" if value else "No"

        if key in ("created_by", "updated_by"):
            return self._format_user(value)

        if key in ("order_date", "invoice_date", "paid_date",
                   "production_date", "expiry_date"):
            return str(value).split("T")[0]

        if key in ("created_at", "updated_at"):
            return self._format_datetime(value)
            
        return str(value)

    @staticmethod
    def _format_user(value) -> str:
        if isinstance(value, dict):
            return (
                value.get("username")
                or value.get("name")
                or value.get("email")
                or str(value.get("id", "—"))
            )
        return str(value)

    @staticmethod
    def _format_datetime(value: str) -> str:
        raw = str(value)
        if "T" in raw:
            date_part, time_part = raw.split("T", 1)
            return f"{date_part} {time_part[:8]}"
        return raw

    def _style_status(self, label: QLabel, status: str) -> None:
        """Apply status colour via QSS property ``status`` (no setStyleSheet)."""
        key = (status or "").lower()
        label.setObjectName("statusLabel")
        label.setProperty("status", key)
        style = label.style()
        if style is not None:
            style.unpolish(label)
            style.polish(label)
        label.update()

    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    def get_data(self) -> dict:
        return dict(self._data)