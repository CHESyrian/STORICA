"""
ui/dialogs/sales_payment_dialog.py

"Add Sales Payment" form dialog.
Records a payment against an existing sales invoice.
"""

from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QDoubleSpinBox, QLabel, QTextEdit
)

from ..base_dialog import BaseFormDialog


class AddSalesPaymentDialog(BaseFormDialog):
    """
    Dialog for recording a payment against a sales invoice.

    Can be opened with a pre-selected invoice (invoice_data) or with
    a list of invoice options for the user to pick from.
    """

    def __init__(
        self,
        invoice_data: dict | None = None,
        invoice_options: dict[str, dict] | None = None,
    ):
        super().__init__("Add Sales Payment", width=650)

        self._invoice_data = invoice_data or {}
        self._invoice_options = invoice_options or {}

        self.invoice_combo = QComboBox()
        if self._invoice_options:
            for label, data in self._invoice_options.items():
                self.invoice_combo.addItem(label, data)
        elif self._invoice_data:
            code = self._invoice_data.get(
                "code", f"INV-{self._invoice_data.get('id', '')}"
            )
            self.invoice_combo.addItem(code, self._invoice_data)
            self.invoice_combo.setEnabled(False)

        self.customer_label = QLabel("—")
        self.total_amount_label = QLabel("—")
        self.amount_paid_label = QLabel("—")
        self.balance_due_label = QLabel("—")

        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setDecimals(2)
        self.amount_spin.setRange(0.01, 1_000_000)
        self.amount_spin.setValue(0)

        self.payment_date_edit = QDateEdit()
        self.payment_date_edit.setCalendarPopup(True)
        self.payment_date_edit.setDate(QDate.currentDate())

        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(80)

        self.build_ui()
        self.connect_signals()
        self._refresh_invoice_display()

    def build_ui(self) -> None:
        self.add_row("Invoice *", self.invoice_combo)
        self.add_row("Customer", self.customer_label)
        self.add_row("Total Amount", self.total_amount_label)
        self.add_row("Already Paid", self.amount_paid_label)
        self.add_row("Balance Due", self.balance_due_label)
        self.add_row("Payment Amount *", self.amount_spin)
        self.add_row("Payment Date", self.payment_date_edit)
        self.add_row("Notes", self.notes_text)
        self.finalize()

    def connect_signals(self) -> None:
        self.invoice_combo.currentIndexChanged.connect(
            self._refresh_invoice_display
        )

    def _selected_invoice(self) -> dict:
        data = self.invoice_combo.currentData()
        return data if isinstance(data, dict) else {}

    def _refresh_invoice_display(self) -> None:
        inv = self._selected_invoice()
        total = float(inv.get("total_amount", 0) or 0)
        paid = float(inv.get("amount_paid", 0) or 0)
        balance = max(total - paid, 0)

        self.customer_label.setText(
            str(inv.get("customer_name") or inv.get("customer") or "—")
        )
        self.total_amount_label.setText(f"{total:,.2f}")
        self.amount_paid_label.setText(f"{paid:,.2f}")
        self.balance_due_label.setText(f"{balance:,.2f}")

        self.amount_spin.setRange(0.01, balance if balance > 0 else 1_000_000)
        if balance > 0:
            self.amount_spin.setValue(balance)

    def validate(self) -> list[str]:
        errors: list[str] = []
        inv = self._selected_invoice()
        if not inv or not inv.get("id"):
            errors.append("Select an invoice.")
        if self.amount_spin.value() <= 0:
            errors.append("Payment amount must be greater than zero.")
        return errors

    def get_data(self) -> dict:
        inv = self._selected_invoice()
        return {
            "invoice": inv.get("id"),
            "order": inv.get("order"),
            "customer": inv.get("customer"),
            "amount": str(self.amount_spin.value()),
            "payment_date": self.payment_date_edit.date().toString(
                "yyyy-MM-dd"
            ),
            "notes": self.notes_text.toPlainText().strip(),
        }
