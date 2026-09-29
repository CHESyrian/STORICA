"""
Panel page for STORICA — quick actions plus closable report tabs.
"""

from PyQt6.QtCore import pyqtSignal

from frontend.ui.widgets import StandardTabWidget
from frontend.ui.tabs import PanelTab, ReportTab


class PanelView(StandardTabWidget):
    """
    Panel page: fixed Quick Actions tab + dynamic closable report tabs.
    """

    panel_tab_selected = pyqtSignal()

    REPORT_TITLES = {
        "inventory": "Inventory Report",
        "stock_movement": "Stock Movement Report",
        "sales": "Sales Report",
        "product_performance": "Product Performance",
        "warehouse_summary": "Warehouse Summary",
        "category_analysis": "Category Analysis",
    }

    def __init__(self):
        super().__init__()
        self._report_tabs: dict[str, int] = {}  # report_type -> tab index
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        self.panel_tab = PanelTab()
        self.add_tab(
            self.panel_tab,
            "⚡ Quick Actions",
            closable=False,
            tooltip="Quick-create entities and generate reports",
        )
        self.set_current_tab(0)

    def connect_signals(self):
        self.tab_changed.connect(self._on_tab_changed)
        self.tab_closed.connect(self._on_tab_closed)
        if hasattr(self.panel_tab, "report_requested"):
            self.panel_tab.report_requested.connect(self.open_report_tab)

    def _on_tab_changed(self, index: int):
        if index == 0:
            self.panel_tab_selected.emit()

    def _on_tab_closed(self, index: int):
        # Rebuild report_type → index map from remaining tabs
        rebuilt: dict[str, int] = {}
        for i in range(self.count()):
            w = self.widget(i)
            if isinstance(w, ReportTab):
                rebuilt[w.report_type] = i
        self._report_tabs = rebuilt

    def open_report_tab(self, report_type: str):
        """Open (or focus) a closable report tab for ``report_type``."""
        title = self.REPORT_TITLES.get(
            report_type, report_type.replace("_", " ").title()
        )

        # Focus existing
        if report_type in self._report_tabs:
            idx = self._report_tabs[report_type]
            if 0 <= idx < self.count() and isinstance(
                self.widget(idx), ReportTab
            ):
                self.setCurrentIndex(idx)
                return

        tab = ReportTab(report_type, title)
        index = self.add_tab(
            tab,
            f"📊 {title}",
            closable=True,
            tooltip=f"Report: {title} (closable)",
            data={"report_type": report_type},
        )
        self._report_tabs[report_type] = index
        self.setCurrentIndex(index)

    def set_current_tab(self, index: int):
        if 0 <= index < self.count():
            self.setCurrentIndex(index)

    def set_panel_tab(self):
        self.set_current_tab(0)

    def get_panel_tab(self) -> PanelTab:
        return self.panel_tab

    def refresh_current_tab(self):
        current_tab = self.currentWidget()
        if hasattr(current_tab, "refresh"):
            current_tab.refresh()
