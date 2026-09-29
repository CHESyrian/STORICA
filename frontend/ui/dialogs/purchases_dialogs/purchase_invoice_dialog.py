"""
ui/dialogs/purchase_invoice_dialog.py

"Add Purchase Invoice" form dialog.

"""

from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QDoubleSpinBox, QHeaderView, 
    QLabel, QLineEdit
)

from frontend.ui.widgets import StandardTable

from frontend.utils.constants import (
    PURCHASE_INVOICE_DETAIL_FIELDS, 
    PURCHASE_INVOICE_ITEMS_COLUMN_MAP,
)

from ..base_dialog import (
    BaseFormDialog, 
    BaseDetailDialog, 
)


ITEM_COLUMNS = [
    "Item ID", "Variant", "Ordered Qty", "Invoice Qty",
    "Cost Price", "Tax %", "Discount %", "Production Date", "Expiry Date",
]
(
    ITEM_ID_COL, VARIANT_COL, ORDERED_COL, QUANTITY_COL,
    COST_PRICE_COL, TAX_COL, DISCOUNT_COL, PRODUCTION_DATE_COL, EXPIRY_DATE_COL,
) = range(9)


class AddPurchaseInvoiceDialog(BaseFormDialog):
    """
    Dialog for recording a Purchase Invoice against an existing
    Purchase Order.

    """

    def __init__(self, order_data: dict, warehouses: list[dict] | None = None,):
        super().__init__("Add Purchase Invoice", width=1050)

        self._order_data  = order_data or {}
        self._warehouses  = warehouses or []
        self._order_id    = self._order_data.get("id")
        self._supplier_id = self._order_data.get("supplier")
        self._items       = self._order_data.get("items", []) or []

        order_code        = self._order_data.get("code", "")
        supplier_name     = self._order_data.get("supplier_name", "")

        self.order_label  = QLabel(f"{order_code}  —  {supplier_name}")

        self.warehouse_combo = QComboBox()

        self.invoice_date_edit = QDateEdit()
        self.invoice_date_edit.setCalendarPopup(True)
        self.invoice_date_edit.setDate(QDate.currentDate())

        # Auto-calculated from the item rows (qty * cost * (1 + tax%) *
        # (1 - discount%)); not user-editable since it must always
        # reflect the line items below.
        self.total_amount_spin = QDoubleSpinBox()
        self.total_amount_spin.setDecimals(2)
        self.total_amount_spin.setRange(0, 999_999_999)
        self.total_amount_spin.setReadOnly(True)
        self.total_amount_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)

        # How much of the total has been paid so far. Capped at
        # total_amount, which is refreshed whenever items change.
        self.amount_paid_spin = QDoubleSpinBox()
        self.amount_paid_spin.setDecimals(2)
        self.amount_paid_spin.setRange(0, 0)

        self.items_table = StandardTable(ITEM_COLUMNS, stretch=False)
        self.items_table.horizontalHeader().setSectionResizeMode(
            VARIANT_COL, QHeaderView.ResizeMode.Stretch
        )
        # Rows hold live spin boxes / combo, not sortable cell values —
        # same rationale as AddPurchaseOrderDialog.items_table.
        self.items_table.setSortingEnabled(False)
        self.items_table.setMinimumHeight(180)

        if self._warehouses:
            self.set_warehouses(self._warehouses)

        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Purchase Order", self.order_label)
        self.add_row("To Warehouse"  , self.warehouse_combo)
        self.add_row("Invoice Date"  , self.invoice_date_edit)
        self.add_row("Items"         , self.items_table)
        self.add_row("Total Amount"  , self.total_amount_spin)
        self.add_row("Amount Paid"   , self.amount_paid_spin)

        self._populate_item_rows()
        self._recalculate_total()

        self.finalize()

    # ------------------------------------------------------------------
    # Data population
    # ------------------------------------------------------------------

    def set_warehouses(self, warehouses: list[dict]) -> None:
        """Populate the product combo box. `products` is (id, name) pairs."""
        self.warehouse_combo.clear()
        
        for warehouse in warehouses:
            self.warehouse_combo.addItem(warehouse['name'], warehouse.get('id'))


    def _populate_item_rows(self) -> None:
        """
        One row per purchase-order line item. Item ID / Variant /
        Ordered Qty are read-only reference widgets sourced from the
        order item; Invoice Qty defaults to (and is capped at) the
        ordered quantity since there's no "already invoiced" figure to
        subtract against. Cost Price / Tax / Discount default to 0 and
        are always editable. Production Date and Expiry Date default to
        today's date and are editable.
        """
        self.items_table.setRowCount(0)
        current_date = QDate.currentDate()

        for item in self._items:
            row = self.items_table.rowCount()
            self.items_table.insertRow(row)

            item_id_edit = QLineEdit(str(item.get("id", "")))
            item_id_edit.setReadOnly(True)
            self.items_table.setCellWidget(row, ITEM_ID_COL, item_id_edit)

            variant_combo = QComboBox()
            variant_combo.addItem(item.get("variant_name", ""), item.get("variant"))
            variant_combo.setEnabled(False)
            self.items_table.setCellWidget(row, VARIANT_COL, variant_combo)

            ordered_qty = float(item.get("quantity") or 0)

            ordered_spin = QDoubleSpinBox()
            ordered_spin.setDecimals(2)
            ordered_spin.setRange(0, ordered_qty)
            ordered_spin.setValue(ordered_qty)
            ordered_spin.setReadOnly(True)
            ordered_spin.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
            self.items_table.setCellWidget(row, ORDERED_COL, ordered_spin)

            quantity_spin = QDoubleSpinBox()
            quantity_spin.setDecimals(2)
            quantity_spin.setRange(0, ordered_qty)
            quantity_spin.setValue(ordered_qty)
            quantity_spin.valueChanged.connect(self._recalculate_total)
            self.items_table.setCellWidget(row, QUANTITY_COL, quantity_spin)

            cost_price_spin = QDoubleSpinBox()
            cost_price_spin.setDecimals(2)
            cost_price_spin.setRange(0, 999_999)
            cost_price_spin.valueChanged.connect(self._recalculate_total)
            self.items_table.setCellWidget(row, COST_PRICE_COL, cost_price_spin)

            tax_spin = QDoubleSpinBox()
            tax_spin.setDecimals(2)
            tax_spin.setRange(0, 100)
            tax_spin.valueChanged.connect(self._recalculate_total)
            self.items_table.setCellWidget(row, TAX_COL, tax_spin)

            discount_spin = QDoubleSpinBox()
            discount_spin.setDecimals(2)
            discount_spin.setRange(0, 100)
            discount_spin.valueChanged.connect(self._recalculate_total)
            self.items_table.setCellWidget(row, DISCOUNT_COL, discount_spin)

            # Production Date
            production_date_edit = QDateEdit()
            production_date_edit.setCalendarPopup(True)
            production_date_edit.setDate(current_date)
            self.items_table.setCellWidget(row, PRODUCTION_DATE_COL, production_date_edit)

            # Expiry Date
            expiry_date_edit = QDateEdit()
            expiry_date_edit.setCalendarPopup(True)
            expiry_date_edit.setDate(current_date.addDays(365))  # Default to 1 year from today
            self.items_table.setCellWidget(row, EXPIRY_DATE_COL, expiry_date_edit)

    # ------------------------------------------------------------------
    # Totals
    # ------------------------------------------------------------------

    def _recalculate_total(self, *_args) -> None:
        """
        Sum each row's line total — qty * cost * (1 + tax%) * (1 -
        discount%) — into total_amount, then re-cap amount_paid so it
        can never exceed the new total.
        """
        total = 0.0
        for row in range(self.items_table.rowCount()):
            quantity_spin   = self.items_table.cellWidget(row, QUANTITY_COL)
            cost_price_spin = self.items_table.cellWidget(row, COST_PRICE_COL)
            tax_spin        = self.items_table.cellWidget(row, TAX_COL)
            discount_spin   = self.items_table.cellWidget(row, DISCOUNT_COL)

            quantity      = quantity_spin.value() if quantity_spin else 0
            cost_price    = cost_price_spin.value() if cost_price_spin else 0
            tax_rate      = tax_spin.value() if tax_spin else 0
            discount_rate = discount_spin.value() if discount_spin else 0

            line_total  = quantity * cost_price
            line_total *= (1 + tax_rate / 100)
            line_total *= (1 - discount_rate / 100)
            total      += line_total

        self.total_amount_spin.setValue(total)
        self.amount_paid_spin.setRange(0, total)

    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self._items:
            errors.append("This purchase order has no items to invoice.")

        total_qty = 0
        for row in range(self.items_table.rowCount()):
            quantity_spin = self.items_table.cellWidget(row, QUANTITY_COL)
            cost_price_spin = self.items_table.cellWidget(row, COST_PRICE_COL)
            production_date_edit = self.items_table.cellWidget(row, PRODUCTION_DATE_COL)
            expiry_date_edit = self.items_table.cellWidget(row, EXPIRY_DATE_COL)

            qty = quantity_spin.value() if quantity_spin else 0
            total_qty += qty

            if qty > 0 and cost_price_spin and cost_price_spin.value() <= 0:
                variant_combo = self.items_table.cellWidget(row, VARIANT_COL)
                variant_name = variant_combo.currentText() if variant_combo else f"row {row + 1}"
                errors.append(f"Cost price must be greater than zero for {variant_name}.")

            # Validate dates
            if production_date_edit and expiry_date_edit:
                prod_date = production_date_edit.date()
                exp_date = expiry_date_edit.date()
                if qty > 0 and prod_date > exp_date:
                    variant_combo = self.items_table.cellWidget(row, VARIANT_COL)
                    variant_name = variant_combo.currentText() if variant_combo else f"row {row + 1}"
                    errors.append(f"Production date must be before expiry date for {variant_name}.")

        if total_qty == 0:
            errors.append("At least one item must have a quantity greater than zero.")

        return errors

    def get_data(self) -> dict:
        items = []

        for row in range(self.items_table.rowCount()):
            variant_combo   = self.items_table.cellWidget(row, VARIANT_COL)
            quantity_spin   = self.items_table.cellWidget(row, QUANTITY_COL)
            cost_price_spin = self.items_table.cellWidget(row, COST_PRICE_COL)
            tax_spin        = self.items_table.cellWidget(row, TAX_COL)
            discount_spin   = self.items_table.cellWidget(row, DISCOUNT_COL)
            production_date_edit = self.items_table.cellWidget(row, PRODUCTION_DATE_COL)
            expiry_date_edit = self.items_table.cellWidget(row, EXPIRY_DATE_COL)

            quantity        = quantity_spin.value() if quantity_spin else 0
            if quantity <= 0:
                continue

            # Get dates as ISO format strings, or None if not set
            production_date = None
            expiry_date = None
            
            if production_date_edit:
                prod_date = production_date_edit.date()
                if prod_date:
                    production_date = prod_date.toPyDate().isoformat()
            
            if expiry_date_edit:
                exp_date = expiry_date_edit.date()
                if exp_date:
                    expiry_date = exp_date.toPyDate().isoformat()

            items.append({
                "variant"        : variant_combo.currentData() if variant_combo else None,
                "quantity"       : quantity,
                "cost_price"     : cost_price_spin.value() if cost_price_spin else 0,
                "tax_rate"       : tax_spin.value() if tax_spin else 0,
                "discount_rate"  : discount_spin.value() if discount_spin else 0,
                "production_date": production_date,
                "expiry_date"    : expiry_date,
            })

        return {
            "order"        : self._order_id, 
            "supplier"     : self._supplier_id, 
            "warehouse"    : self.warehouse_combo.currentData(), 
            "invoice_date" : self.invoice_date_edit.date().toPyDate().isoformat(),
            "total_amount" : self.total_amount_spin.value(),
            "amount_paid"  : self.amount_paid_spin.value(),
            "items"        : items,
        }


