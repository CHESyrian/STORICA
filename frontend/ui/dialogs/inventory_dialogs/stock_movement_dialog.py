"""
ui/dialogs/stock_movement_dialog.py

Add Stock Movement form dialog (created as PENDING).
"""

from __future__ import annotations

from PyQt6.QtWidgets import QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit

from ..base_dialog import BaseFormDialog


class AddStockMovementDialog(BaseFormDialog):
    """Dialog for creating a PENDING stock movement."""

    def __init__(self):
        super().__init__("Add Stock Movement")

        self.type_combo = QComboBox()
        self.type_combo.addItems(["in", "out", "transfer", "adjustment", "return"])

        self.product_combo = QComboBox()
        self.batch_combo = QComboBox()
        self.from_wh_combo = QComboBox()
        self.to_wh_combo = QComboBox()

        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 1_000_000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setValue(1)

        self.unit_price_spin = QDoubleSpinBox()
        self.unit_price_spin.setRange(0, 1_000_000)
        self.unit_price_spin.setDecimals(2)

        self.reference_edit = QLineEdit()
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)

        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Type *", self.type_combo)
        self.add_row("Product *", self.product_combo)
        self.add_row("Batch", self.batch_combo)
        self.add_row("From Warehouse", self.from_wh_combo)
        self.add_row("To Warehouse", self.to_wh_combo)
        self.add_row("Quantity *", self.quantity_spin)
        self.add_row("Unit Price", self.unit_price_spin)
        self.add_row("Reference", self.reference_edit)
        self.add_row("Notes", self.notes_edit)
        self.finalize()

    def set_product_options(self, options: dict[str, int]) -> None:
        self.product_combo.clear()
        for label, pk in options.items():
            self.product_combo.addItem(label, pk)

    def set_batch_options(self, options: dict[str, int]) -> None:
        self.batch_combo.clear()
        self.batch_combo.addItem("—", None)
        for label, pk in options.items():
            self.batch_combo.addItem(label, pk)

    def set_warehouse_options(self, options: dict[str, int]) -> None:
        for combo in (self.from_wh_combo, self.to_wh_combo):
            combo.clear()
            combo.addItem("—", None)
            for label, pk in options.items():
                combo.addItem(label, pk)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.product_combo.currentData() is None:
            errors.append("Product is required.")
        if self.quantity_spin.value() <= 0:
            errors.append("Quantity must be positive.")
        if self.type_combo.currentText() == "transfer":
            if self.to_wh_combo.currentData() is None:
                errors.append("Transfer requires a destination warehouse.")
        return errors

    def get_data(self) -> dict:
        data = {
            "movement_type": self.type_combo.currentText(),
            "product": self.product_combo.currentData(),
            "quantity": str(self.quantity_spin.value()),
            "unit_price": str(self.unit_price_spin.value()),
            "reference_number": self.reference_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
        }
        if self.batch_combo.currentData() is not None:
            data["batch"] = self.batch_combo.currentData()
        if self.from_wh_combo.currentData() is not None:
            data["from_warehouse"] = self.from_wh_combo.currentData()
        if self.to_wh_combo.currentData() is not None:
            data["to_warehouse"] = self.to_wh_combo.currentData()
        return data
