"""Add / edit user dialogs and profile / password dialogs."""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QLineEdit, QLabel,
)

from ..base_dialog import BaseFormDialog


ROLES = ["admin", "manager", "user", "viewer", "guest"]


class AddUserDialog(BaseFormDialog):
    def __init__(self):
        super().__init__("Add User")
        self.username_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.full_name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItems(ROLES)
        self.role_combo.setCurrentText("user")
        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Username", self.username_edit)
        self.add_row("Email", self.email_edit)
        self.add_row("Full name", self.full_name_edit)
        self.add_row("Password", self.password_edit)
        self.add_row("Confirm", self.confirm_edit)
        self.add_row("Role", self.role_combo)
        self.finalize()

    def get_data(self) -> dict:
        return {
            "username": self.username_edit.text().strip(),
            "email": self.email_edit.text().strip() or None,
            "full_name": self.full_name_edit.text().strip(),
            "password": self.password_edit.text(),
            "confirm_password": self.confirm_edit.text(),
            "role": self.role_combo.currentText(),
        }

    def validate(self) -> tuple[bool, str]:
        d = self.get_data()
        if not d["username"]:
            return False, "Username is required."
        if len(d["password"] or "") < 8:
            return False, "Password must be at least 8 characters."
        if d["password"] != d["confirm_password"]:
            return False, "Passwords do not match."
        return True, ""


class EditUserDialog(BaseFormDialog):
    def __init__(self, user: dict | None = None):
        super().__init__("Edit User")
        self.user = user or {}
        self.email_edit = QLineEdit(self.user.get("email") or "")
        self.full_name_edit = QLineEdit(self.user.get("full_name") or "")
        self.role_combo = QComboBox()
        self.role_combo.addItems(ROLES)
        role = self.user.get("role") or "user"
        if role in ROLES:
            self.role_combo.setCurrentText(role)
        self.active_check = QCheckBox("Active")
        self.active_check.setChecked(bool(self.user.get("is_active", True)))
        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Email", self.email_edit)
        self.add_row("Full name", self.full_name_edit)
        self.add_row("Role", self.role_combo)
        self.add_row("", self.active_check)
        self.finalize()

    def get_data(self) -> dict:
        return {
            "email": self.email_edit.text().strip() or None,
            "full_name": self.full_name_edit.text().strip(),
            "role": self.role_combo.currentText(),
            "is_active": self.active_check.isChecked(),
        }


class ProfileDialog(BaseFormDialog):
    def __init__(self, user: dict | None = None):
        super().__init__("My Profile")
        self.user = user or {}
        self.email_edit = QLineEdit(self.user.get("email") or "")
        self.full_name_edit = QLineEdit(self.user.get("full_name") or "")
        self.theme_edit = QLineEdit(self.user.get("theme") or "light")
        self.language_edit = QLineEdit(self.user.get("language") or "en")
        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Email", self.email_edit)
        self.add_row("Full name", self.full_name_edit)
        self.add_row("Theme", self.theme_edit)
        self.add_row("Language", self.language_edit)
        self.finalize()

    def get_data(self) -> dict:
        return {
            "email": self.email_edit.text().strip() or None,
            "full_name": self.full_name_edit.text().strip(),
            "theme": self.theme_edit.text().strip() or "light",
            "language": self.language_edit.text().strip() or "en",
        }


class ChangePasswordDialog(BaseFormDialog):
    def __init__(self):
        super().__init__("Change Password")
        self.old_edit = QLineEdit()
        self.old_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_edit = QLineEdit()
        self.new_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("Current password", self.old_edit)
        self.add_row("New password", self.new_edit)
        self.add_row("Confirm", self.confirm_edit)
        self.finalize()

    def get_data(self) -> dict:
        return {
            "old_password": self.old_edit.text(),
            "new_password": self.new_edit.text(),
            "confirm_password": self.confirm_edit.text(),
        }

    def validate(self) -> tuple[bool, str]:
        d = self.get_data()
        if len(d["new_password"] or "") < 8:
            return False, "New password must be at least 8 characters."
        if d["new_password"] != d["confirm_password"]:
            return False, "Passwords do not match."
        return True, ""


class ResetPasswordDialog(BaseFormDialog):
    def __init__(self, username: str = ""):
        super().__init__(f"Reset Password — {username}" if username else "Reset Password")
        self.new_edit = QLineEdit()
        self.new_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.build_ui()

    def build_ui(self) -> None:
        self.add_row("New password", self.new_edit)
        self.add_row("Confirm", self.confirm_edit)
        self.finalize()

    def get_data(self) -> dict:
        return {
            "new_password": self.new_edit.text(),
            "confirm_password": self.confirm_edit.text(),
        }

    def validate(self) -> tuple[bool, str]:
        d = self.get_data()
        if len(d["new_password"] or "") < 8:
            return False, "Password must be at least 8 characters."
        if d["new_password"] != d["confirm_password"]:
            return False, "Passwords do not match."
        return True, ""
