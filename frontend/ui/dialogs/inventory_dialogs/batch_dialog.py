"""
ui/dialogs/batch_dialog.py

Add/Edit Batch form dialog.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QLineEdit, QComboBox, QDoubleSpinBox, QDateEdit
from PyQt6.QtCore import QDate

from ..base_dialog import BaseFormDialog


class AddBatchDialog(BaseFormDialog):
    """Dialog for creating a Batch (variant + warehouse stock lot)."""

    def __init__(self):
        super().__init__("Add Batch")

        self.variant_combo = QComboBox()
        self.warehouse_combo = QComboBox()
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 1_000_000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setValue(1)

        self.cost_spin = QDoubleSpinBox()
        self.cost_spin.setRange(0, 1_000_000)
        self.cost_spin.setDecimals(2)

        self.production_date = QDateEdit()
        self.production_date.setCalendarPopup(True)
        self.production_date.setDate(QDate.currentDate())

        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDate(QDate.currentDate().addYears(1))
        self.expiry_date.setSpecialValueText("None")

        self.status_combo = QComboBox()
        self.status_combo.addItems(["active", "expired", "recalled", "sold_out"])

        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Variant *", self.variant_combo)
        self.add_row("Warehouse *", self.warehouse_combo)
        self.add_row("Quantity *", self.quantity_spin)
        self.add_row("Cost Price *", self.cost_spin)
        self.add_row("Production Date *", self.production_date)
        self.add_row("Expiry Date", self.expiry_date)
        self.add_row("Status", self.status_combo)
        self.finalize()

    def set_variant_options(self, options: dict[str, int]) -> None:
        """options: display_label -> id"""
        self.variant_combo.clear()
        for label, pk in options.items():
            self.variant_combo.addItem(label, pk)

    def set_warehouse_options(self, options: dict[str, int]) -> None:
        self.warehouse_combo.clear()
        for label, pk in options.items():
            self.warehouse_combo.addItem(label, pk)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.variant_combo.currentData() is None:
            errors.append("Variant is required.")
        if self.warehouse_combo.currentData() is None:
            errors.append("Warehouse is required.")
        if self.quantity_spin.value() <= 0:
            errors.append("Quantity must be positive.")
        return errors

    def get_data(self) -> dict:
        exp = self.expiry_date.date()
        return {
            "variant": self.variant_combo.currentData(),
            "warehouse": self.warehouse_combo.currentData(),
            "quantity": str(self.quantity_spin.value()),
            "cost_price": str(self.cost_spin.value()),
            "production_date": self.production_date.date().toString("yyyy-MM-dd"),
            "expiry_date": exp.toString("yyyy-MM-dd") if exp.isValid() else None,
            "status": self.status_combo.currentText(),
        }
