"""
ui/dialogs/variant_dialog.py

"Add Variant" form dialog.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QComboBox, QDoubleSpinBox, QLineEdit

from ..base_dialog import BaseFormDialog
from frontend.utils.constants import MAX_DIMENSION


def _make_spinbox(suffix: str = "") -> QDoubleSpinBox:
    """Build a QDoubleSpinBox with sane bounds/precision for dimensions."""
    spin = QDoubleSpinBox()
    spin.setRange(0.0, MAX_DIMENSION)
    spin.setDecimals(2)

    if suffix:
        spin.setSuffix(f" {suffix}")

    return spin


class AddVariantDialog(BaseFormDialog):
    """
    Dialog for creating/editing a Product Variant.

    NOTE: `save_btn.clicked` is intentionally left unconnected here.
    The owning controller connects it to its own create/update handler
    (see BaseTab._run_create), calls `validate()` itself, and decides
    when to close the dialog based on the APIResult. Do not connect
    save_btn or call accept()/close() inside this class.
    """

    def __init__(self, products: list[dict] | None = None):
        super().__init__("Add Variant")

        self._products = products

        self.product_combo = QComboBox()
        self.name_edit     = QLineEdit()
        self.color_edit    = QLineEdit()
        self.weight_spin   = _make_spinbox("kg")
        self.length_spin   = _make_spinbox("cm")
        self.width_spin    = _make_spinbox("cm")
        self.height_spin   = _make_spinbox("cm")
        self.min_stock_spin = _make_spinbox()
        self.min_stock_spin.setDecimals(2)

        if self._products:
            self.set_products(self._products)

        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Product", self.product_combo)
        self.add_row("Name"   , self.name_edit)
        self.add_row("Color"  , self.color_edit)
        self.add_row("Weight" , self.weight_spin)
        self.add_row("Length" , self.length_spin)
        self.add_row("Width"  , self.width_spin)
        self.add_row("Height" , self.height_spin)
        self.add_row("Min Stock", self.min_stock_spin)
        self.finalize()

    def set_products(self, products: list[tuple[int, str]]) -> None:
        """Populate the product combo box. `products` is (id, name) pairs."""
        self.product_combo.clear()
        
        for product in products:
            self.product_combo.addItem(product['name'], product.get('id'))

    def validate(self) -> list[str]:
        errors: list[str] = []

        if self.product_combo.currentData() is None:
            errors.append("A product must be selected.")

        return errors

    def get_data(self) -> dict:
        def _dim(spin: QDoubleSpinBox):
            val = spin.value()
            return None if val == 0.0 else val

        return {
            "product": self.product_combo.currentData(),
            "name": self.name_edit.text().strip(),
            "color": self.color_edit.text().strip() or None,
            "weight": _dim(self.weight_spin),
            "length": _dim(self.length_spin),
            "width": _dim(self.width_spin),
            "height": _dim(self.height_spin),
            "min_stock": self.min_stock_spin.value(),
        }

