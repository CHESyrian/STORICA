"""
ui/dialogs/purchases_order_dialog.py

"Add Purchases Order" form dialog.
"""

from __future__ import annotations

from PyQt6.QtCore import QDate, QSize
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QHeaderView, QLineEdit, QWidget,
    QToolButton, QPushButton, QSpinBox, QVBoxLayout, 
)

from frontend.ui.widgets import StandardTable, color_icon

from frontend.utils.constants import (
    Icon, Color, 
    PURCHASE_ORDER_DETAIL_FIELDS, 
    PURCHASE_ORDER_ITEMS_COLUMN_MAP
)

from ..base_dialog import (
    BaseFormDialog, 
    BaseDetailDialog, 
)


ITEM_COLUMNS = ["Variant", "Quantity", ""]
VARIANT_COL, QUANTITY_COL, REMOVE_COL = range(3)


class AddPurchaseOrderDialog(BaseFormDialog):
    """
    Dialog for creating a Purchases Order with line items.

    NOTE: `save_btn.clicked` is intentionally left unconnected here.
    The owning controller connects it to its own create handler
    (see BaseTab._run_create), calls `validate()` itself, and decides
    when to close the dialog based on the APIResult. Do not connect
    save_btn or call accept()/close() inside this class.
    """

    def __init__(
        self,
        suppliers: list[dict] | None = None,
        variants: list[dict] | None = None,
    ):
        super().__init__("Add Purchases Order", width=780)

        self._suppliers = suppliers or []
        self._variants  = variants or []

        self.supplier_combo = QComboBox()

        self.order_date_edit = QDateEdit()
        self.order_date_edit.setCalendarPopup(True)
        self.order_date_edit.setDate(QDate.currentDate())

        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Optional notes")

        # stretch=False: StandardTable's default stretches the *last*
        # section, but our last column is the empty Remove-button
        # column. We stretch Variant instead, below.
        self.items_table = StandardTable(ITEM_COLUMNS, stretch=False)
        self.items_table.horizontalHeader().setSectionResizeMode(
            VARIANT_COL, QHeaderView.ResizeMode.Stretch
        )

        # StandardTable defaults to sorting enabled, which is meant for
        # read-only display tables. This table's rows hold live combo
        # boxes / spin boxes / buttons rather than sortable cell values,
        # so sorting would silently reorder widgets out from under the
        # user. Keep it off.
        self.items_table.setSortingEnabled(False)
        self.items_table.setMinimumHeight(160)

        self.add_item_btn = QPushButton("Add Item")
        self.add_item_btn.clicked.connect(self.add_item_row)

        if self._suppliers:
            self.set_suppliers(self._suppliers)

        if self._variants:
            self.set_variants(self._suppliers)

        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Supplier", self.supplier_combo)
        self.add_row("Order Date", self.order_date_edit)
        self.add_row("Notes", self.notes_edit)

        items_container = QWidget()
        items_layout = QVBoxLayout()
        items_layout.setContentsMargins(0, 0, 0, 0)
        items_layout.addWidget(self.items_table)
        items_layout.addWidget(self.add_item_btn)
        items_container.setLayout(items_layout)
        self.add_row("Items", items_container)

        # Start with one empty item row so the dialog isn't blank.
        self.add_item_row()

        self.finalize()

    # ------------------------------------------------------------------
    # Data population
    # ------------------------------------------------------------------

    def set_suppliers(self, suppliers: list[dict]) -> None:
        """Populate the supplier combo box. `suppliers` is a list of {'id', 'name'} dicts."""
        self.supplier_combo.clear()

        for supplier in suppliers:
            self.supplier_combo.addItem(supplier["name"], supplier["id"])

    def set_variants(self, variants: list[dict]) -> None:
        """
        Store the available variants and refresh any item rows already
        on the table. `variants` is a list of {'id', 'name'} dicts.
        """

        for row in range(self.items_table.rowCount()):
            combo = self.items_table.cellWidget(row, VARIANT_COL)
            if combo is not None:
                self._populate_variant_combo(combo)

    def _populate_variant_combo(self, combo: QComboBox) -> None:
        combo.clear()

        for variant in self._variants:
            combo.addItem(variant["name"], variant["id"])

    # ------------------------------------------------------------------
    # Item row helpers
    # ------------------------------------------------------------------

    def add_item_row(self) -> None:
        row = self.items_table.rowCount()
        self.items_table.insertRow(row)

        variant_combo = QComboBox()
        self._populate_variant_combo(variant_combo)
        self.items_table.setCellWidget(row, VARIANT_COL, variant_combo)

        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 999999)
        quantity_spin.setValue(1)
        self.items_table.setCellWidget(row, QUANTITY_COL, quantity_spin)

        remove_btn = QToolButton()
        remove_btn.setObjectName('deleteIcon')
        remove_btn.setIcon(
            color_icon(Icon.TRASH_2, Color.COLOR_GY01)
        )
        remove_btn.setIconSize(QSize(20, 20))
        remove_btn.clicked.connect(lambda: self._remove_item_row(remove_btn))
        self.items_table.setCellWidget(row, REMOVE_COL, remove_btn)

    def _remove_item_row(self, remove_btn: QPushButton) -> None:
        for row in range(self.items_table.rowCount()):
            if self.items_table.cellWidget(row, REMOVE_COL) is remove_btn:
                self.items_table.removeRow(row)
                return

    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    def validate(self) -> list[str]:
        errors: list[str] = []

        if self.supplier_combo.currentData() is None:
            errors.append("A supplier must be selected.")

        seen_variant_ids = set()
        item_count = 0
        for row in range(self.items_table.rowCount()):
            variant_combo = self.items_table.cellWidget(row, VARIANT_COL)
            variant_id = variant_combo.currentData() if variant_combo else None
            if variant_id is None:
                continue

            item_count += 1
            if variant_id in seen_variant_ids:
                errors.append("Duplicate variants are not allowed in the same order.")
            seen_variant_ids.add(variant_id)

        if item_count == 0:
            errors.append("Order must have at least one item.")

        return errors

    def get_data(self) -> dict:
        items = []
        for row in range(self.items_table.rowCount()):
            variant_combo = self.items_table.cellWidget(row, VARIANT_COL)
            quantity_spin = self.items_table.cellWidget(row, QUANTITY_COL)

            variant_id = variant_combo.currentData() if variant_combo else None
            if variant_id is None:
                continue

            items.append({
                "variant": variant_id,
                "quantity": quantity_spin.value() if quantity_spin else 1,
            })

        return {
            "supplier": self.supplier_combo.currentData(),
            "order_date": self.order_date_edit.date().toPyDate().isoformat(),
            "notes": self.notes_edit.text().strip(),
            "items": items,
        }


# =======================================================================================


class ViewPurchaseOrderDialog(BaseDetailDialog):
    """Read-only "View Purchase Order" dialog."""

    FIELDS = PURCHASE_ORDER_DETAIL_FIELDS

    def __init__(self, data: dict):
        super().__init__("Purchase Order Details", data, width=780)

    def build_ui(self) -> None:
        for label, key in self.FIELDS.items():
            self.add_row(label, self._make_field(key))

        self.add_items_table(
            "Items", self._data.get("items", []), PURCHASE_ORDER_ITEMS_COLUMN_MAP
        )

        self.finalize_readonly()



