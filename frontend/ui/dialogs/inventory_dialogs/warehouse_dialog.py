"""
ui/dialogs/warehouse_dialog.py

"Add Warehouse" form dialog.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QCheckBox, QLineEdit

from ..base_dialog import BaseFormDialog
from frontend.utils.validators import is_valid_phone


class AddWarehouseDialog(BaseFormDialog):
    """
    Dialog for creating/editing a Warehouse.

    NOTE: `save_btn.clicked` is intentionally left unconnected here.
    The owning controller connects it to its own create/update handler
    (see BaseTab._run_create), calls `validate()` itself, and decides
    when to close the dialog based on the APIResult. Do not connect
    save_btn or call accept()/close() inside this class.
    """

    def __init__(self):
        super().__init__("Add Warehouse")

        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        self.location_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.status_check = QCheckBox("Active")
        self.status_check.setChecked(True)

        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Name *", self.name_edit)
        self.add_row("Description", self.description_edit)
        self.add_row("Location", self.location_edit)
        self.add_row("Phone *", self.phone_edit)
        self.add_row("Status", self.status_check)
        self.finalize()

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self.name_edit.text().strip():
            errors.append("Name is required.")

        phone = self.phone_edit.text().strip()
        if not phone:
            errors.append("Phone is required.")
        elif not is_valid_phone(phone):
            errors.append("Phone number is not valid.")

        return errors

    def get_data(self) -> dict:
        return {
            "name"       : self.name_edit.text().strip(),
            "description": self.description_edit.text().strip(),
            "location"   : self.location_edit.text().strip(),
            "phone"      : self.phone_edit.text().strip(),
            "status"     : (
                "active" 
                if self.status_check.isChecked() 
                else "inactive"
            ),
        }
