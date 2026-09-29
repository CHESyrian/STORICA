"""
Sales page for STORICA application.
Fixed tab widget with non-removable, non-closable tabs.

Mirrors purchases_view.py exactly, with SuppliersTab swapped for
CustomersTab. See that file for the purchasing-side twin.

NOTE: assumes a CustomersTab widget exists in frontend.ui.tabs,
parallel to SuppliersTab. It isn't included here since it wasn't
part of what was supplied for this pass.
"""

from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import pyqtSignal

from frontend.api import APIClient

from frontend.ui.widgets import StandardTabWidget

from frontend.ui.tabs import (
    SalesOrderTab,
    SalesInvoiceTab,
    CustomersTab,
    SalesPaymentsTab,
)


class SalesView(StandardTabWidget):
    """
    Sales management page with fixed static tabs.
    Inherits from StandardTabWidget - SalesView IS a tab widget.
    Tabs are fixed and cannot be added, removed, moved, or closed.
    """

    # Signals for tab changes
    sales_orders_tab_selected = pyqtSignal()
    invoices_tab_selected     = pyqtSignal()
    customers_tab_selected    = pyqtSignal()
    payments_tab_selected     = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the sales page with fixed static tabs."""

        self.sales_order_tab = SalesOrderTab()
        self.invoice_tab     = SalesInvoiceTab()
        self.customer_tab    = CustomersTab()
        self.payments_tab    = SalesPaymentsTab()

        self.add_tab(
            self.sales_order_tab,
            "📋 Orders",
            closable=False,
            tooltip="Manage sales orders"
        )

        self.add_tab(
            self.invoice_tab,
            "📦 Invoices",
            closable=False,
            tooltip="Manage sales invoices"
        )

        self.add_tab(
            self.customer_tab,
            "🧑‍🤝‍🧑 Customers",
            closable=False,
            tooltip="Manage customers"
        )

        self.add_tab(
            self.payments_tab,
            "💳 Payments",
            closable=False,
            tooltip="Manage sales payments"
        )

        self.set_current_tab(0)

    def connect_signals(self):
        """Connect internal signals."""
        self.tab_changed.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int):
        """Handle tab change and emit appropriate signals."""
        if index == 0:
            self.sales_orders_tab_selected.emit()
        elif index == 1:
            self.invoices_tab_selected.emit()
        elif index == 2:
            self.customers_tab_selected.emit()
        elif index == 3:
            self.payments_tab_selected.emit()

    def set_current_tab(self, index: int):
        """Set the currently active tab by index."""
        if 0 <= index < self.count():
            self.setCurrentIndex(index)

    def set_sales_orders_tab(self):
        self.set_current_tab(0)

    def set_invoices_tab(self):
        self.set_current_tab(1)

    def set_customers_tab(self):
        self.set_current_tab(2)

    def set_payments_tab(self):
        self.set_current_tab(3)

    def get_sales_order_tab(self) -> QWidget:
        return self.sales_order_tab

    def get_invoice_tab(self) -> QWidget:
        return self.invoice_tab

    def get_customer_tab(self) -> QWidget:
        return self.customer_tab

    def get_payments_tab(self) -> QWidget:
        return self.payments_tab

    def refresh_all_tabs(self):
        self.sales_order_tab.refresh()
        self.invoice_tab.refresh()
        self.customer_tab.refresh()
        self.payments_tab.refresh()

    def refresh_current_tab(self):
        current_tab = self.currentWidget()
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh()
