"""
Purchases page for STORICA application.
Fixed tab widget with non-removable, non-closable tabs.
"""

from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import pyqtSignal

from frontend.api import APIClient

from frontend.ui.widgets import StandardTabWidget

from frontend.ui.tabs import (
    PurchasesOrderTab, 
    PurchasesInvoiceTab, 
    PaymentsTab, 
    SuppliersTab
)


class PurchasesView(StandardTabWidget):
    """
    Purchases management page with fixed static tabs.
    Inherits from StandardTabWidget - PurchasesView IS a tab widget.
    Tabs are fixed and cannot be added, removed, moved, or closed.
    """
    
    # Signals for tab changes
    purchase_orders_tab_selected = pyqtSignal()
    invoices_tab_selected        = pyqtSignal()
    suppliers_tab_selected       = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Setup the purchases page with fixed static tabs."""
        
        # Create all tab widgets
        self.purchase_order_tab  = PurchasesOrderTab()
        self.invoice_tab         = PurchasesInvoiceTab()
        self.payments_tab        = PaymentsTab()
        self.supplier_tab        = SuppliersTab()
        
        # Add fixed tabs (closable=False is already enforced by setTabsClosable)
        
        self.add_tab(
            self.purchase_order_tab, 
            "📋 Orders", 
            closable=False, 
            tooltip="Manage purchase orders"
        )
        
        self.add_tab(
            self.invoice_tab, 
            "📦 Invoices", 
            closable=False, 
            tooltip="Manage purchase invoices"
        )

        self.add_tab(
            self.payments_tab, 
            "💳 Payments", 
            closable=False, 
            tooltip="Manage purchase payments"
        )
        
        self.add_tab(
            self.supplier_tab, 
            "🏢 Suppliers", 
            closable=False, 
            tooltip="Manage suppliers"
        )
        
        # Set initial active tab (Dashboard tab at index 0)
        self.set_current_tab(0)
        
    def connect_signals(self):
        """Connect internal signals."""
        # Connect tab change signals
        self.tab_changed.connect(self._on_tab_changed)
        
    def _on_tab_changed(self, index: int):
        """Handle tab change and emit appropriate signals."""
        if index == 0:
            self.purchase_orders_tab_selected.emit()

        elif index == 1:
            self.invoices_tab_selected.emit()

        elif index == 2:
            self.suppliers_tab_selected.emit()
            
    # Convenience methods for navigation
    def set_current_tab(self, index: int):
        """Set the currently active tab by index."""
        if 0 <= index < self.count():
            self.setCurrentIndex(index)
        
    def set_purchase_orders_tab(self):
        """Switch to purchase orders tab."""
        self.set_current_tab(0)
        
    def set_invoices_tab(self):
        """Switch to invoices tab."""
        self.set_current_tab(1)
        
    def set_suppliers_tab(self):
        """Switch to suppliers tab."""
        self.set_current_tab(2)
        
    # Getter methods for each tab    
    def get_purchase_order_tab(self) -> QWidget:
        """Get the purchase orders tab widget."""
        return self.purchase_order_tab
    
    def get_invoice_tab(self) -> QWidget:
        """Get the invoices tab widget."""
        return self.invoice_tab
    
    def get_supplier_tab(self) -> QWidget:
        """Get the suppliers tab widget."""
        return self.supplier_tab
    
    # Refresh methods
    def refresh_all_tabs(self):
        """Refresh data in all tabs."""
        self.purchase_order_tab.refresh()
        self.invoice_tab.refresh()
        self.supplier_tab.refresh()
    
    def refresh_current_tab(self):
        """Refresh only the currently active tab."""
        current_tab = self.currentWidget()
        if hasattr(current_tab, 'refresh'):
            current_tab.refresh()