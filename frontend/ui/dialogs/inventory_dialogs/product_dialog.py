"""
ui/dialogs/product_dialog.py

"Add Product" form dialog.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox, QFileDialog, QHBoxLayout, QLineEdit,
    QPushButton, QTextEdit, QWidget
)

from ..base_dialog import BaseFormDialog
from frontend.utils.constants import (
    IMAGE_FILTER, UNIT_CHOICES
)


class AddProductDialog(BaseFormDialog):
    """
    Dialog for creating/editing a Product.

    NOTE: `save_btn.clicked` is intentionally left unconnected here.
    The owning controller connects it to its own create/update handler
    (see BaseTab._run_create), calls `validate()` itself, and decides
    when to close the dialog based on the APIResult. Do not connect
    save_btn or call accept()/close() inside this class.
    """

    def __init__(
        self,
        categories: list[dict] | None = None,
    ):
        super().__init__("Add Product")

        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        self.category_combo = QComboBox()
        self.unit_combo = QComboBox()
        self.image_edit = QLineEdit()
        self.image_edit.setReadOnly(True)
        self.image_btn = QPushButton("Browse...")
        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(80)

        self.image_btn.clicked.connect(self._pick_image)

        self.set_categories(categories)
        self.set_units(UNIT_CHOICES)
        
        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Name", self.name_edit)
        self.add_row("Description", self.description_edit)
        self.add_row("Category", self.category_combo)
        self.add_row("Unit", self.unit_combo)
        self.add_row("Image", self._image_row())
        self.add_row("Notes", self.notes_edit)
        self.finalize()

    def _image_row(self) -> QWidget:
        """Wrap the image path field + browse button into one row widget."""
        row = QWidget()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_edit)
        layout.addWidget(self.image_btn)
        return row

    def _pick_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", IMAGE_FILTER
        )
        if path:
            self.image_edit.setText(path)

    def set_categories(self, categories: list[tuple[int, str]]) -> None:
        """Populate the category combo. `categories` is (id, name) pairs."""
        self.category_combo.clear()
        for category in categories:
            self.category_combo.addItem(category['name'], category['id'])

    def set_units(self, units: list[tuple[int, str]]) -> None:
        """Populate the unit combo box. `units` is (id, name) pairs."""
        self.unit_combo.clear()
        for unit in units:
            self.unit_combo.addItem(unit[1], unit[0])

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self.name_edit.text().strip():
            errors.append("Name is required.")

        return errors

    def get_data(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.text().strip(),
            "category": self.category_combo.currentData(),
            "unit": self.unit_combo.currentData(),
            "image_path": self.image_edit.text().strip() or None,
            "notes": self.notes_edit.toPlainText().strip(),
        }
