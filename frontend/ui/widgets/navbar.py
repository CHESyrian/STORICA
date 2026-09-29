from typing import Any
from collections.abc import Mapping

from PyQt6.QtCore import QDate, QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox,QDateEdit,QHBoxLayout,QLabel,
    QLineEdit, QPushButton, QToolButton, QWidget,
)

from frontend.utils.constants import Icon, Color
from .custom_icons import color_icon


class Navbar(QWidget):
    """
    Reusable toolbar / navigation bar for list views.

    All child components are created up front; callers control which ones
    are visible via ``set_components_visible()``, ``show_component()``, etc.

    Signals:
        search_changed(str):            Emitted as the user types in the search box.
        filter_changed(str, str):       Emitted with (combo_name, selected_text).
        date_range_changed(QDate, QDate): Emitted when either date changes.
        refresh_clicked():              Emitted when the refresh button is clicked.
    """

    search_changed     = pyqtSignal(str)
    choice_changed     = pyqtSignal(object)
    status_changed     = pyqtSignal(object)
    active_changed     = pyqtSignal(bool)
    flag_changed       = pyqtSignal(bool)
    date_range_changed = pyqtSignal(QDate, QDate)
    button_1_clicked   = pyqtSignal()
    button_2_clicked   = pyqtSignal()
    button_3_clicked   = pyqtSignal()
    button_4_clicked   = pyqtSignal()
    button_5_clicked   = pyqtSignal()
    refresh_clicked    = pyqtSignal()

    def __init__(self, view) -> None:
        super().__init__()
        self.view = view
        self._components: dict[str, QWidget] = {}
        self._build_ui()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)

        # Action icon buttons
        self.button_1 = QToolButton()  # Add 1
        self.button_2 = QToolButton()  # Add 2
        self.button_3 = QToolButton()  # Edit
        self.button_4 = QToolButton()  # Delete
        self.button_5 = QToolButton()  # Export

        for btn in (
            self.button_1,
            self.button_2,
            self.button_3,
            self.button_4,
            self.button_5,
        ):
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName('navIcon')

        # Search field
        self.search = QLineEdit()
        self.search.setPlaceholderText("🔍 Search...")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self.search_changed)

        # Filter combo boxes
        self.choice = QComboBox()
        self.status = QComboBox()
        
        # Filter Active checkbox
        self.active = QCheckBox("Active")
        self.active.setChecked(True)

        # Generic secondary flag checkbox (label set by the owning tab)
        self.flag = QCheckBox("Flag")
        self.flag.setChecked(False)

        # From Date
        self.from_label = QLabel("From:")
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-6))
        self.date_from.setDisplayFormat("yyyy-MM-dd")

        #To Date
        self.to_label = QLabel("To:")
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("yyyy-MM-dd")

        # Refresh button
        self.refresh_btn = QToolButton()
        self.refresh_btn.setObjectName('navIcon')
        self.refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_btn.setIcon(color_icon(Icon.REFRESH_CCW, Color.COLOR_GR06))
        self.refresh_btn.setIconSize(QSize(28, 28))
        
        # Register all components for bulk visibility management
        self._components = {
            "button_1"   : self.button_1,
            "button_2"   : self.button_2,
            "button_3"   : self.button_3,
            "button_4"   : self.button_4,
            "button_5"   : self.button_5,
            "search"     : self.search,
            "choice"     : self.choice,
            "status"     : self.status, 
            "active"     : self.active,
            "flag"       : self.flag,
            "from_label" : self.from_label,
            "date_from"  : self.date_from,
            "to_label"   : self.to_label,
            "date_to"    : self.date_to,
            "refresh_btn": self.refresh_btn,
        }

        self.hide_all_components()

        # Signals
        self.button_1.clicked.connect(self.button_1_clicked.emit)
        self.button_2.clicked.connect(self.button_2_clicked.emit)
        self.button_3.clicked.connect(self.button_3_clicked.emit)
        self.button_4.clicked.connect(self.button_4_clicked.emit)
        self.button_5.clicked.connect(self.button_5_clicked.emit)

        self.choice.currentIndexChanged.connect(
            lambda _: self.choice_changed.emit(
                self.choice.currentData()
            )
        )

        self.status.currentIndexChanged.connect(
            lambda _: self.status_changed.emit(
                self.status.currentData()
            )
        )

        self.active.toggled.connect(self.active_changed)
        self.flag.toggled.connect(self.flag_changed)

        self.date_from.dateChanged.connect(self._on_date_changed)
        self.date_to.dateChanged.connect(self._on_date_changed)
        self.refresh_btn.clicked.connect(self.refresh_clicked)

        # Add widgets to layout
        for btn in (
            self.button_1,
            self.button_2,
            self.button_3,
            self.button_4,
            self.button_5,
        ):
            layout.addWidget(btn)

        layout.addWidget(self.search)
        layout.addWidget(self.choice)
        layout.addWidget(self.status)
        layout.addWidget(self.active)
        layout.addWidget(self.flag)
        layout.addWidget(self.from_label)
        layout.addWidget(self.date_from)
        layout.addWidget(self.to_label)
        layout.addWidget(self.date_to)
        layout.addStretch()
        layout.addWidget(self.refresh_btn)

    # ------------------------------------------------------------------
    # Button factory
    # ------------------------------------------------------------------

    def configure_icon_button(
        self,
        button: QToolButton,
        name: str,
        icon_path: str,
        icon_color: str,
        tooltip: str = "",
    ) -> None:
        """
        Apply an icon, object name, and tooltip to one of the toolbar buttons.

        Args:
            button:     One of ``self.button_1`` … ``self.button_5``.
            name:       Object name (also used as the ``icon_clicked`` payload).
            icon_path:  Path passed to ``color_icon()``.
            icon_color: Colour passed to ``color_icon()``.
            tooltip:    Optional tooltip string.
        """
        
        button.setObjectName(name)
        button.setIcon(color_icon(icon_path, icon_color))
        button.setIconSize(QSize(26, 26))
        if tooltip:
            button.setToolTip(tooltip)

    # ------------------------------------------------------------------
    # Visibility management
    # ------------------------------------------------------------------

    def show_component(self, name: str) -> None:
        """Make a single component visible by name."""
        if name in self._components:
            self._components[name].setVisible(True)

    def hide_component(self, name: str) -> None:
        """Hide a single component by name."""
        if name in self._components:
            self._components[name].setVisible(False)

    def set_components_visible(self, names: list[str]) -> None:
        """Show only the named components; hide everything else."""
        visible = set(names)
        for name, widget in self._components.items():
            widget.setVisible(name in visible)

    def hide_all_components(self) -> None:
        """Hide every managed component."""
        for widget in self._components.values():
            widget.setVisible(False)

    # Convenience presets ---------------------------------------------------

    def show_default_setup(self) -> None:
        """Show the most common set of controls."""
        self.set_components_visible(
            ["button_1", "button_2", "button_3", "button_4",
             "search", "status", "refresh_btn"]
        )

    def show_search_filters(self) -> None:
        """Show search, filter combos, date range, and refresh."""
        self.set_components_visible(
            ["search", "choice", "status", "active", 
             "from_label", "date_from", "to_label", "date_to",
             "refresh_btn"]
        )

    def show_full_setup(self) -> None:
        """Make every managed component visible."""
        self.set_components_visible(list(self._components.keys()))

    # ------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------

    def get_search_text(self) -> str:
        return self.search.text()

    def get_choice_filter(self) -> str:
        return self.choice.currentData()

    def get_status_filter(self) -> str:
        return self.status.currentData()

    def get_active_checked(self) -> bool:
        return self.active.isChecked()

    def get_flag_checked(self) -> bool:
        return self.flag.isChecked()

    def configure_flag(
        self,
        label: str,
        *,
        tooltip: str = "",
        checked: bool = False,
    ) -> None:
        """Set the reusable flag checkbox label/tooltip for this tab."""
        self.flag.setText(label)
        self.flag.setToolTip(tooltip or "")
        self.flag.setChecked(checked)

    def get_date_from(self) -> QDate:
        return self.date_from.date()

    def get_date_to(self) -> QDate:
        return self.date_to.date()

    def get_all_filters(self) -> dict:
        """Return all current filter values as a plain dict."""
        return {
            "search"   : self.get_search_text(),
            "choice"   : self.get_choice_filter(),
            "status"   : self.get_status_filter(),
            "active"   : self.get_active_checked(),
            "flag"     : self.get_flag_checked(),
            "date_from": self.get_date_from().toString("yyyy-MM-dd"),
            "date_to"  : self.get_date_to().toString("yyyy-MM-dd"),
        }

    def get_visible_components(self) -> list[str]:
        """Return names of all currently visible components."""
        return [
            name
            for name, widget in self._components.items()
            if widget.isVisible()
        ]

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------

    def set_search_text(self, text: str) -> None:
        self.search.setText(text)

    def set_choice_items(self, items: list[str] | Mapping[Any, Any]) -> None:
        """Replace choice combo items without emitting ``choice_changed``."""
        self.choice.blockSignals(True)
        try:
            self.choice.clear()
            if isinstance(items, Mapping):
                for key, value in items.items():
                    self.choice.addItem(str(value), userData=key)
            else:
                for item in items:
                    self.choice.addItem(item)
        finally:
            self.choice.blockSignals(False)

    def set_status_items(self, items: list[str] | Mapping[Any, Any]) -> None:
        """Replace status combo items without emitting ``status_changed``."""
        self.status.blockSignals(True)
        try:
            self.status.clear()
            if isinstance(items, Mapping):
                for key, value in items.items():
                    self.status.addItem(str(value), userData=key)
            else:
                for item in items:
                    self.status.addItem(item)
        finally:
            self.status.blockSignals(False)

    def populate_combo(self, combo, items: list[str] | list[tuple[str, Any]]) -> None:
        """Replace combo items without emitting ``currentIndexChanged``."""
        combo.blockSignals(True)
        try:
            combo.clear()
            for item in items:
                if isinstance(item, tuple):
                    combo.addItem(item[0], item[1])
                else:
                    combo.addItem(item)
        finally:
            combo.blockSignals(False)

    def set_date_range(self, from_date: QDate, to_date: QDate) -> None:
        self.date_from.setDate(from_date)
        self.date_to.setDate(to_date)

    def clear_all_filters(self) -> None:
        """Reset every filter control to its default state."""
        self.search.clear()
        self.status.setCurrentIndex(0)
        self.choice.setCurrentIndex(0)
        self.active.setChecked(True)
        self.flag.setChecked(False)
        self.date_from.setDate(QDate.currentDate().addMonths(-6))
        self.date_to.setDate(QDate.currentDate())

    # ------------------------------------------------------------------
    # Loading / busy state
    # ------------------------------------------------------------------
    
    def set_loading_state(self, loading: bool) -> None:
        """Toggle a visual 'loading' state on the refresh button."""
        if loading:
            self.refresh_btn.setText("⏳ Loading…")
            self.refresh_btn.setEnabled(False)
        else:
            self.refresh_btn.setText("🔄 Refresh")
            self.refresh_btn.setEnabled(True)

    # ------------------------------------------------------------------
    # Private slots
    # ------------------------------------------------------------------

    def _on_date_changed(self, _date: QDate) -> None:
        self.date_range_changed.emit(
            self.date_from.date(), 
            self.date_to.date()
        )
