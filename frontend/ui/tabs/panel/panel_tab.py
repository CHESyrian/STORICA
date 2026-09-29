"""
ui/panel_tab.py

Panel tab widget containing grid of quick-create and report buttons.
Each button opens a dialog or generates a report, and on action
runs the matching controller method through AsyncExecutor.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QPushButton, QGridLayout, QSizePolicy, QLabel, 
    QHBoxLayout, QVBoxLayout
)
from PyQt6.QtCore import QSize, Qt, pyqtSignal

from frontend.api import APIResult, ApiWorker, AsyncExecutor

from frontend.ui.widgets import (
    color_icon, LoadingOverlay
)

from frontend.utils.dialog_handler import DialogHandler
from frontend.utils.managers import MessageManager
from frontend.utils.constants import (
    Color, Icon
)

from frontend.controllers import PanelController

from frontend.ui.dialogs import (
    AddCategoryDialog, AddWarehouseDialog,
    AddCustomerDialog, AddProductDialog,
    AddVariantDialog, AddSupplierDialog
)


class PanelTab(QWidget):
    """
    Widget containing grid of quick-create and report buttons.
    This is the content displayed inside the panel tab.
    """

    report_requested = pyqtSignal(str)

    # Fixed tile size so every button has identical width regardless of label.
    BUTTON_WIDTH      = 168
    BUTTON_HEIGHT     = 140
    GRID_SPACING      = 15
    GRID_MARGIN       = 10

    def __init__(self):
        super().__init__()
        self.panel_controller = PanelController()
        self.msg_manager      = MessageManager()
        self.executor         = AsyncExecutor()
        self.overlay          = LoadingOverlay(self)
        self.dialog_handler   = DialogHandler(
            executor=self.executor,
            overlay=self.overlay,
            message_manager=self.msg_manager,
        )
        
        self._create_dialogs = {
            "category": (
                AddCategoryDialog,
                lambda self: (
                    self.get_all_data("categories").data.get("data", []),
                ),
                self.panel_controller.create_category,
                "Category",
            ),
            "warehouse": (
                AddWarehouseDialog,
                lambda self: (),
                self.panel_controller.create_warehouse,
                "Warehouse",
            ),
            "supplier": (
                AddSupplierDialog,
                lambda self: (),
                self.panel_controller.create_supplier,
                "Supplier",
            ),
            "customer": (
                AddCustomerDialog,
                lambda self: (),
                self.panel_controller.create_customer,
                "Customer",
            ),
            "product": (
                AddProductDialog,
                lambda self: (
                    self.get_all_data("categories").data["data"],
                ),
                self.panel_controller.create_product,
                "Product",
            ),
            "variant": (
                AddVariantDialog,
                lambda self: (
                    self.get_all_data("products").data["data"],
                ),
                self.panel_controller.create_variant,
                "Variant",
            ),
        }
        
        self.setObjectName("panel_page")
        self._build_ui()

    def _build_ui(self):
        """Build the grid of quick-create and report buttons."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

        # Quick Create Section
        create_label = QLabel("Quick Create")
        create_label.setObjectName("panelSectionLabel")
        create_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(create_label)

        self._create_grid = QGridLayout()
        self._create_grid.setSpacing(self.GRID_SPACING)

        create_buttons = [
            (
                'Category',
                color_icon(Icon.FILE_PLUS, Color.COLOR_BU06),
                self.category_dialog
            ),
            (
                'Warehouse',
                color_icon(Icon.FILE_PLUS, Color.COLOR_YE02),
                self.warehouse_dialog
            ),
            (
                'Product',
                color_icon(Icon.FILE_PLUS, Color.COLOR_GR10),
                self.product_dialog
            ),
            (
                'Variant',
                color_icon(Icon.FILE_PLUS, Color.COLOR_YE03),
                self.variant_dialog
            ),
            (
                'Supplier',
                color_icon(Icon.FILE_PLUS, Color.COLOR_PI09),
                self.supplier_dialog
            ),
            (
                'Customer',
                color_icon(Icon.FILE_PLUS, Color.COLOR_PU08),
                self.customer_dialog
            ),
        ]

        self._create_widgets = self._build_grid_buttons(create_buttons)
        main_layout.addLayout(self._create_grid)

        # Separator
        separator = QWidget()
        separator.setObjectName("panelSeparator")
        separator.setFixedHeight(2)
        main_layout.addWidget(separator)

        # Reports Section
        reports_label = QLabel("Reports")
        reports_label.setObjectName("panelSectionLabel")
        reports_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(reports_label)

        self._reports_grid = QGridLayout()
        self._reports_grid.setSpacing(self.GRID_SPACING)

        reports_buttons = [
            (
                'Inventory',
                color_icon(Icon.CHART_BAR, Color.COLOR_BU06),
                self.inventory_report
            ),
            (
                'Stock Move',
                color_icon(Icon.CHART_BAR, Color.COLOR_YE02),
                self.stock_movement_report
            ),
            (
                'Sales',
                color_icon(Icon.CHART_BAR, Color.COLOR_GR10),
                self.sales_report
            ),
            (
                'Performance',
                color_icon(Icon.CHART_BAR, Color.COLOR_YE03),
                self.product_performance
            ),
            (
                'Warehouses',
                color_icon(Icon.CHART_BAR, Color.COLOR_PI09),
                self.warehouse_summary
            ),
            (
                'Categories',
                color_icon(Icon.CHART_BAR, Color.COLOR_PU08),
                self.category_analysis
            ),
        ]

        self._reports_widgets = self._build_grid_buttons(reports_buttons)
        main_layout.addLayout(self._reports_grid)

        # Add stretch to push content to the top
        #main_layout.addStretch()

        self._reflow_grids()

    def _build_grid_buttons(self, buttons) -> list[QPushButton]:
        """
        Build the button widgets for a grid, without placing them.

        Placement (row/column) is decided by `_reflow_grid` based on
        the widget's current width, so it can be recomputed whenever
        the tab is resized instead of being fixed at build time.
        """
        widgets = []

        for text, icon, func in buttons:
            btn = QPushButton()
            btn.setText(text)
            btn.setIcon(icon)
            btn.setIconSize(QSize(32, 32))
            # Fixed size so label length never changes button width.
            btn.setFixedSize(self.BUTTON_WIDTH, self.BUTTON_HEIGHT)
            btn.setSizePolicy(
                QSizePolicy.Policy.Fixed,
                QSizePolicy.Policy.Fixed,
            )

            btn.clicked.connect(func)
            widgets.append(btn)

        return widgets

    def _reflow_grid(self, grid_layout: QGridLayout, widgets: list[QPushButton]) -> None:
        """Re-place `widgets` into `grid_layout` using as many columns as fit."""
        if not widgets:
            return

        available_width = self.width() - (2 * self.GRID_MARGIN)
        column_width = self.BUTTON_WIDTH + self.GRID_SPACING
        columns = max(1, (available_width + self.GRID_SPACING) // column_width)
        columns = min(columns, len(widgets))

        # Detach widgets from the layout without deleting them, then
        # re-add at their new row/column - takeAt(0) repeatedly drains
        # the layout since indices shift down as items are removed.
        while grid_layout.count():
            grid_layout.takeAt(0)

        row = col = 0
        for widget in widgets:
            grid_layout.addWidget(widget, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def _reflow_grids(self) -> None:
        """Recompute column counts for both button grids from the current width."""
        self._reflow_grid(self._create_grid, self._create_widgets)
        self._reflow_grid(self._reports_grid, self._reports_widgets)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self._reflow_grids()

        if self.overlay:
            self.overlay.setGeometry(self.rect())

    def get_all_data(self, model: str):
        """Fetch all data for a given model."""
        self.overlay.show()
        data = self.panel_controller.get_all(model)
        self.overlay.hide()
        return data

    # -----------------------------------------------------------------
    # Open Dialog
    # -----------------------------------------------------------------
    def open_create_dialog(self, name):
        """Open a create dialog for the specified entity."""
        dialog_cls, args_fn, create_fn, label = self._create_dialogs[name]

        dialog = dialog_cls(*args_fn(self))

        self.dialog_handler.open(
            dialog=dialog,
            create_fn=create_fn,
            entity_name=label,
        )

    # ===============================
    # Dialog Launchers (Quick Create)
    # ===============================
    def category_dialog(self):
        self.open_create_dialog("category")

    def warehouse_dialog(self):
        self.open_create_dialog("warehouse")

    def product_dialog(self):
        self.open_create_dialog("product")

    def variant_dialog(self):
        self.open_create_dialog("variant")

    def supplier_dialog(self):
        self.open_create_dialog("supplier")

    def customer_dialog(self):
        self.open_create_dialog("customer")

    # -----------------------------------------------------------------
    # Report Generation Methods
    # -----------------------------------------------------------------
    def generate_report(self, report_type: str):
        """Open a closable report tab in PanelView (no dialog)."""
        self.report_requested.emit(report_type)

    # ============================
    # Report Launchers
    # ============================
    def inventory_report(self):
        self.generate_report("inventory")
    
    def stock_movement_report(self):
        self.generate_report("stock_movement")
    
    def sales_report(self):
        self.generate_report("sales")
    
    def product_performance(self):
        self.generate_report("product_performance")
    
    def warehouse_summary(self):
        self.generate_report("warehouse_summary")
    
    def category_analysis(self):
        self.generate_report("category_analysis")

    def refresh(self):
        """Refresh the panel tab content if needed."""
        # Currently no data to refresh in the grid view
        pass