"""
Stacked content manager for STORICA.
Manages all application pages/views.
"""

from PyQt6.QtWidgets import (
    QStackedWidget, QWidget
)

from frontend.ui.views import (
    InventoryView, PurchasesView, SalesView, PanelView, UsersView
)
from frontend.ui.widgets import StoricaWidget

class StackContent(QStackedWidget):
    """Manages all application content pages."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.page_order = ["storica", "inventory", "purchases", "sales", "users", "panel"]

        self.page_config = {
            "storica"   : StoricaWidget(), 
            "inventory" : InventoryView(), 
            "purchases" : PurchasesView(),
            "sales"     : SalesView(),
            "users"     : UsersView(),
            "panel"     : PanelView(),
        }
        self._setup_pages()

    def _setup_pages(self):
        """Initialize all application pages in order."""
        for page_name in self.page_order:
            page = self.page_config[page_name]
            self.addWidget(page)

    def show_page(self, name: str):
        """Switch to a page by name."""
        if name in self.page_order:
            self.setCurrentIndex(self.page_order.index(name))


