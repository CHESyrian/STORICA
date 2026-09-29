"""
ui/dialogs/sales_dialogs/sales_invoice_dialog.py

"Add Sales Invoice" form dialog.

Records an invoice against an existing Sales Order. Takes the full
order payload (as returned by SalesController.get_sales_order, via
SalesOrderTab.get_current_order_data) and pre-fills one invoice-item
row per order line: Item ID / Variant / Ordered Qty are read-only
reference columns pulled from the order item, while Invoice Qty /
Unit Price / Tax / Discount are editable and become the invoice item
payload.

Mirrors AddPurchaseInvoiceDialog, with the counterparty swapped from
supplier -> customer and cost_price -> unit_price (this is the price
charged to the customer, not a purchasing cost). See
purchase_invoice_dialog.py for the purchasing-side twin.

NOTE: invoice items reference `variant` directly (there is no
order-item FK on the invoice item model), so line matching for the
payload is by variant, not by order-item id.
"""

from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QDoubleSpinBox, QHeaderView,
    QLabel, QLineEdit
)

from frontend.ui.widgets import StandardTable

from ..base_dialog import BaseFormDialog


ITEM_COLUMNS = [
    "Item ID", "Variant", "Ordered Qty", "Invoice Qty",
    "Unit Price", "Tax %", "Discount %",
]
(
    ITEM_ID_COL, VARIANT_COL, ORDERED_COL, QUANTITY_COL,
    UNIT_PRICE_COL, TAX_COL, DISCOUNT_COL,
) = range(7)


class AddSalesInvoiceDialog(BaseFormDialog):
    """
    Dialog for recording a Sales Invoice against an existing
    Sales Order.

    NOTE: `save_btn.clicked` is intentionally left unconnected here.
    The owning controller connects it to its own create handler
    (see BaseTab._run_create), calls `validate()` itself, and decides
    when to close the dialog based on the APIResult. Do not connect
    save_btn or call accept()/close() inside this class.
    """

    def __init__(self, order_data: dict):
        super().__init__("Add Sales Invoice", width=945)

        self._order_data  = order_data or {}
        self._order_id    = self._order_data.get("id")
        self._customer_id = self._order_data.get("customer")
        self._items       = self._order_data.get("items", []) or []

        order_code    = self._order_data.get("code", "")
        customer_name = self._order_data.get("customer_name", "")

        self.order_label = QLabel(f"{order_code}  —  {customer_name}")

        self.invoice_date_edit = QDateEdit()
        self.invoice_date_edit.setCalendarPopup(True)
        self.invoice_date_edit.setDate(QDate.currentDate())

        # Auto-calculated from the item rows (qty * price * (1 + tax%) *
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
        # same rationale as AddSalesOrderDialog.items_table.
        self.items_table.setSortingEnabled(False)
        self.items_table.setMinimumHeight(180)

        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Sales Order" , self.order_label)
        self.add_row("Invoice Date", self.invoice_date_edit)
        self.add_row("Items"       , self.items_table)
        self.add_row("Total Amount", self.total_amount_spin)
        self.add_row("Amount Paid" , self.amount_paid_spin)

        self._populate_item_rows()
        self._recalculate_total()

        self.finalize()

    # ------------------------------------------------------------------
    # Data population
    # ------------------------------------------------------------------

    def _populate_item_rows(self) -> None:
        """
        One row per sales-order line item. Item ID / Variant / Ordered
        Qty are read-only reference widgets sourced from the order
        item; Invoice Qty defaults to (and is capped at) the ordered
        quantity since there's no "already invoiced" figure to
        subtract against. Unit Price / Tax / Discount default to 0
        and are always editable.
        """
        self.items_table.setRowCount(0)

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

            unit_price_spin = QDoubleSpinBox()
            unit_price_spin.setDecimals(2)
            unit_price_spin.setRange(0, 999_999)
            # Prefill from order line (unit_price or sale_price)
            default_price = float(
                item.get("unit_price")
                or item.get("sale_price")
                or 0
            )
            unit_price_spin.setValue(default_price)
            unit_price_spin.valueChanged.connect(self._recalculate_total)
            self.items_table.setCellWidget(row, UNIT_PRICE_COL, unit_price_spin)

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

    # ------------------------------------------------------------------
    # Totals
    # ------------------------------------------------------------------

    def _recalculate_total(self, *_args) -> None:
        """
        Sum each row's line total — qty * price * (1 + tax%) * (1 -
        discount%) — into total_amount, then re-cap amount_paid so it
        can never exceed the new total.
        """
        total = 0.0
        for row in range(self.items_table.rowCount()):
            quantity_spin   = self.items_table.cellWidget(row, QUANTITY_COL)
            unit_price_spin = self.items_table.cellWidget(row, UNIT_PRICE_COL)
            tax_spin        = self.items_table.cellWidget(row, TAX_COL)
            discount_spin   = self.items_table.cellWidget(row, DISCOUNT_COL)

            quantity      = quantity_spin.value() if quantity_spin else 0
            unit_price    = unit_price_spin.value() if unit_price_spin else 0
            tax_rate      = tax_spin.value() if tax_spin else 0
            discount_rate = discount_spin.value() if discount_spin else 0

            line_total  = quantity * unit_price
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
            errors.append("This sales order has no items to invoice.")

        total_qty = 0
        for row in range(self.items_table.rowCount()):
            quantity_spin = self.items_table.cellWidget(row, QUANTITY_COL)
            unit_price_spin = self.items_table.cellWidget(row, UNIT_PRICE_COL)

            qty = quantity_spin.value() if quantity_spin else 0
            total_qty += qty

            if qty > 0 and unit_price_spin and unit_price_spin.value() <= 0:
                variant_combo = self.items_table.cellWidget(row, VARIANT_COL)
                variant_name = variant_combo.currentText() if variant_combo else f"row {row + 1}"
                errors.append(f"Unit price must be greater than zero for {variant_name}.")

        if total_qty == 0:
            errors.append("At least one item must have a quantity greater than zero.")

        return errors

    def get_data(self) -> dict:
        items = []
        for row in range(self.items_table.rowCount()):
            variant_combo   = self.items_table.cellWidget(row, VARIANT_COL)
            quantity_spin   = self.items_table.cellWidget(row, QUANTITY_COL)
            unit_price_spin = self.items_table.cellWidget(row, UNIT_PRICE_COL)
            tax_spin        = self.items_table.cellWidget(row, TAX_COL)
            discount_spin   = self.items_table.cellWidget(row, DISCOUNT_COL)

            quantity = quantity_spin.value() if quantity_spin else 0
            if quantity <= 0:
                continue

            items.append({
                "variant"       : variant_combo.currentData() if variant_combo else None,
                "quantity"      : quantity,
                # Backend SalesInvoiceItem expects sale_price
                "sale_price"    : unit_price_spin.value() if unit_price_spin else 0,
                "tax_rate"      : tax_spin.value() if tax_spin else 0,
                "discount_rate" : discount_spin.value() if discount_spin else 0,
            })

        return {
            "order"        : self._order_id,
            "customer"     : self._customer_id,
            "invoice_date" : self.invoice_date_edit.date().toPyDate().isoformat(),
            "total_amount" : self.total_amount_spin.value(),
            "amount_paid"  : self.amount_paid_spin.value(),
            "items"        : items,
        }
