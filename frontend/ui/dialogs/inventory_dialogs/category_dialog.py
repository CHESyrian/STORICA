"""
ui/dialogs/category_dialog.py

"Add Category" form dialog.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QLineEdit, QComboBox

from ..base_dialog import BaseFormDialog


class AddCategoryDialog(BaseFormDialog):
    """
    Dialog for creating/editing a Category.

    NOTE: `save_btn.clicked` is intentionally left unconnected here.
    The owning controller connects it to its own create/update handler
    (see BaseTab._run_create), calls `validate()` itself, and decides
    when to close the dialog based on the APIResult. Do not connect
    save_btn or call accept()/close() inside this class.
    """

    def __init__(self, categories: list[dict] | None = None):
        super().__init__("Add Category")

        self._categories = categories

        self.parent_combo = QComboBox()
        self.name_edit = QLineEdit()

        if self._categories:
            self.set_categories(self._categories)

        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Parent", self.parent_combo)
        self.add_row("Name"  , self.name_edit)
        self.finalize()

    def set_categories(self, categories: list[dict]) -> None:
        """Populate the product combo box. `products` is (id, name) pairs."""
        self.parent_combo.clear()
        self.parent_combo.addItem(None, None)
        
        for category in categories:
            self.parent_combo.addItem(category['name'], category.get('id'))

    def validate(self) -> list[str]:
        """Return a list of human-readable errors, empty if the form is valid."""
        errors: list[str] = []

        if not self.name_edit.text().strip():
            errors.append("Name is required.")

        return errors

    def get_data(self) -> dict:
        return {
            "parent" : self.parent_combo.currentData(), 
            "name"   : self.name_edit.text().strip(),
        }
