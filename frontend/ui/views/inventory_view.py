"""
Inventory page for STORICA application.
Fixed tab widget with non-removable, non-closable tabs.
"""

from PyQt6.QtCore import pyqtSignal

from frontend.ui.widgets import StandardTabWidget
from frontend.ui.tabs import (
    ProductTab,
    VariantTab,
    CategoryTab,
    WarehouseTab,
    StockMovementTab,
    BatchTab,
    StockStatusTab,
)


class InventoryView(StandardTabWidget):
    """
    Inventory management page with fixed static tabs.
    Inherits from StandardTabWidget - InventoryView IS a tab widget.
    Tabs are fixed and cannot be added, removed, moved, or closed.
    """

    products_tab_selected = pyqtSignal()
    categories_tab_selected = pyqtSignal()
    variants_tab_selected = pyqtSignal()
    warehouses_tab_selected = pyqtSignal()
    batches_tab_selected = pyqtSignal()
    stock_movements_tab_selected = pyqtSignal()
    stock_status_tab_selected = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the inventory page with fixed static tabs."""
        self.category_tab = CategoryTab()
        self.products_tab = ProductTab()
        self.variant_tab = VariantTab()
        self.warehouse_tab = WarehouseTab()
        self.batch_tab = BatchTab()
        self.stock_movement_tab = StockMovementTab()
        self.stock_status_tab = StockStatusTab()

        self.add_tab(
            self.category_tab,
            "📂 Categories",
            closable=False,
            tooltip="Manage product categories",
        )
        self.add_tab(
            self.products_tab,
            "📦 Products",
            closable=False,
            tooltip="Manage products",
        )
        self.add_tab(
            self.variant_tab,
            "🏷️ Variants",
            closable=False,
            tooltip="Manage product variants",
        )
        self.add_tab(
            self.warehouse_tab,
            "🏠 Warehouses",
            closable=False,
            tooltip="Manage warehouses",
        )
        self.add_tab(
            self.batch_tab,
            "📋 Batches",
            closable=False,
            tooltip="Manage product batches",
        )
        self.add_tab(
            self.stock_movement_tab,
            "📊 Stock Movements",
            closable=False,
            tooltip="View and complete stock movements",
        )
        self.add_tab(
            self.stock_status_tab,
            "📈 Stock Status",
            closable=False,
            tooltip="On-hand stock by variant and warehouse",
        )

        self.set_current_tab(0)

    def connect_signals(self):
        """Connect internal signals."""
        self.tab_changed.connect(self._on_tab_changed)

    def _on_tab_changed(self, index: int):
        """Handle tab change and emit appropriate signals."""
        mapping = {
            0: self.categories_tab_selected,
            1: self.products_tab_selected,
            2: self.variants_tab_selected,
            3: self.warehouses_tab_selected,
            4: self.batches_tab_selected,
            5: self.stock_movements_tab_selected,
            6: self.stock_status_tab_selected,
        }
        signal = mapping.get(index)
        if signal is not None:
            signal.emit()

    def set_current_tab(self, index: int):
        """Set the currently active tab by index."""
        if 0 <= index < self.count():
            self.setCurrentIndex(index)

    def set_categories_tab(self):
        self.set_current_tab(0)

    def set_products_tab(self):
        self.set_current_tab(1)

    def set_variants_tab(self):
        self.set_current_tab(2)

    def set_warehouses_tab(self):
        self.set_current_tab(3)

    def set_batches_tab(self):
        self.set_current_tab(4)

    def set_stock_movements_tab(self):
        self.set_current_tab(5)

    def set_stock_status_tab(self):
        self.set_current_tab(6)

    def get_category_tab(self) -> CategoryTab:
        return self.category_tab

    def get_products_tab(self) -> ProductTab:
        return self.products_tab

    def get_variant_tab(self) -> VariantTab:
        return self.variant_tab

    def get_warehouse_tab(self) -> WarehouseTab:
        return self.warehouse_tab

    def get_batch_tab(self) -> BatchTab:
        return self.batch_tab

    def get_stock_movement_tab(self) -> StockMovementTab:
        return self.stock_movement_tab

    def get_stock_status_tab(self) -> StockStatusTab:
        return self.stock_status_tab

    def refresh_all_tabs(self):
        """Refresh data in all tabs."""
        self.category_tab.refresh()
        self.products_tab.refresh()
        self.variant_tab.refresh()
        self.warehouse_tab.refresh()
        self.batch_tab.refresh()
        self.stock_movement_tab.refresh()
        self.stock_status_tab.refresh()

    def refresh_current_tab(self):
        """Refresh only the currently active tab."""
        current_tab = self.currentWidget()
        if hasattr(current_tab, "refresh"):
            current_tab.refresh()
