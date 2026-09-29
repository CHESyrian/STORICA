"""
ui/dialogs/purchase_payment_dialog.py

"Add Purchase Payment" form dialog.

Records a payment against an existing purchase invoice.
"""

from __future__ import annotations

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QComboBox, QDateEdit, QDoubleSpinBox, QLabel, QTextEdit
)

from ..base_dialog import BaseFormDialog


class AddPurchasePaymentDialog(BaseFormDialog):
    """
    Dialog for recording a payment against a specific Purchase Invoice.

    Displays invoice details (read-only) and allows entering payment
    amount, payment date, and optional notes.
    """

    def __init__(self, invoice_data: dict | None = None):
        super().__init__("Add Purchase Payment", width=650)

        self._invoice_data  = invoice_data or {}
        self._invoice_id    = self._invoice_data.get("id")
        self._order_id      = self._invoice_data.get("order")
        self._supplier_id   = self._invoice_data.get("supplier")
        
        # Extract display values
        invoice_code  = self._invoice_data.get("code", f"INV-{self._invoice_id or ''}")
        supplier_name = self._invoice_data.get("supplier_name", "")
        # Values
        self._total_amount  = float(self._invoice_data.get("total_amount", 0))
        self._amount_paid   = float(self._invoice_data.get("amount_paid", 0))
        self._balance_due   = float(self._total_amount - self._amount_paid)

        # Read-only display fields
        self.invoice_label = QLabel(invoice_code)
        self.supplier_label = QLabel(supplier_name)
        self.total_amount_label = QLabel(f"${self._total_amount:,.2f}")
        self.amount_paid_label = QLabel(f"${self._amount_paid:,.2f}")
        self.balance_due_label = QLabel(f"${self._balance_due:,.2f}")

        # Payment fields
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setDecimals(2)
        self.amount_spin.setRange(0, self._balance_due)
        self.amount_spin.setValue(0)

        self.new_due = QLabel()

        self.payment_date_edit = QDateEdit()
        self.payment_date_edit.setCalendarPopup(True)
        self.payment_date_edit.setDate(QDate.currentDate())

        self.notes_text = QTextEdit()
        self.notes_text.setMaximumHeight(80)

        self.build_ui()
        self.connect_signals()

    def build_ui(self) -> None:
        """Build the dialog UI."""
        self.add_row("Invoice"     , self.invoice_label)
        self.add_row("Supplier"    , self.supplier_label)
        self.add_row("Total Amount", self.total_amount_label)
        self.add_row("Amount Paid" , self.amount_paid_label)
        self.add_row("Balance Due" , self.balance_due_label)
        self.add_separator()
        self.add_row("Payment Amount", self.amount_spin)
        self.add_row("Stay"          , self.new_due)
        self.add_row("Payment Date"  , self.payment_date_edit)
        self.add_row("Notes"         , self.notes_text)

        self.finalize()

    def connect_signals(self) -> None:
        """Connect signals."""
        self.amount_spin.valueChanged.connect(self._on_amount_changed)

    # ------------------------------------------------------------------
    # Signal handlers
    # ------------------------------------------------------------------

    def _on_amount_changed(self, value: float) -> None:
        """Handle payment amount change - cap at balance due."""

        if value > self._balance_due:
            self.amount_spin.setValue(self._balance_due)

        due = self._balance_due - value
        self.new_due.setText(
            str(due if due > 0 else 0)
        )


    # ------------------------------------------------------------------
    # Subclass contract
    # ------------------------------------------------------------------

    def validate(self) -> list[str]:
        """Validate the dialog data."""
        errors: list[str] = []

        if self._invoice_id is None:
            errors.append("No invoice selected for payment.")

        amount = self.amount_spin.value()
        if amount <= 0:
            errors.append("Payment amount must be greater than zero.")

        if amount > self._balance_due:
            errors.append(
                f"Payment amount (${amount:,.2f}) exceeds "
                f"balance due (${self._balance_due:,.2f})."
            )

        return errors

    def get_data(self) -> dict:
        """Get the dialog data as a dictionary."""
        return {
            "invoice"     : self._invoice_id,
            "order"       : self._order_id,
            "supplier"    : self._supplier_id,
            "amount"      : self.amount_spin.value(),
            "payment_date": self.payment_date_edit.date().toPyDate().isoformat(),
            "notes"       : self.notes_text.toPlainText().strip() or "No Notes",
        }