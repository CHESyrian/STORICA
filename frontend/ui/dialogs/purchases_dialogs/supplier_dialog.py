"""
ui/dialogs/supplier_dialog.py

"Add Supplier" form dialog.
"""

from __future__ import annotations

from PyQt6.QtWidgets import QCheckBox, QLineEdit, QTextEdit

from ..base_dialog import BaseFormDialog

from frontend.utils.validators import (
    is_valid_email, 
    is_valid_phone
)


class AddSupplierDialog(BaseFormDialog):
    """
    Dialog for creating/editing a Supplier.

    NOTE: `save_btn.clicked` is intentionally left unconnected here.
    The owning controller connects it to its own create/update handler
    (see BaseTab._run_create), calls `validate()` itself, and decides
    when to close the dialog based on the APIResult. Do not connect
    save_btn or call accept()/close() inside this class.
    """

    def __init__(self):
        super().__init__("Add Supplier")

        self.name_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.address_edit = QLineEdit()
        self.is_verified_check = QCheckBox("Verified")
        self.notes_edit = QTextEdit()
        self.notes_edit.setFixedHeight(80)

        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Name", self.name_edit)
        self.add_row("Email", self.email_edit)
        self.add_row("Phone", self.phone_edit)
        self.add_row("Address", self.address_edit)
        self.add_row("Verified", self.is_verified_check)
        self.add_row("Notes", self.notes_edit)
        self.finalize()

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self.name_edit.text().strip():
            errors.append("Name is required.")

        email = self.email_edit.text().strip()
        if email and not is_valid_email(email):
            errors.append("Email is not valid.")

        phone = self.phone_edit.text().strip()
        if phone and not is_valid_phone(phone):
            errors.append("Phone number is not valid.")

        return errors

    def get_data(self) -> dict:
        return {
            "name": self.name_edit.text().strip(),
            "email": self.email_edit.text().strip(),
            "phone": self.phone_edit.text().strip(),
            "address": self.address_edit.text().strip(),
            "is_verified": self.is_verified_check.isChecked(),
            "notes": self.notes_edit.toPlainText().strip(),
        }
