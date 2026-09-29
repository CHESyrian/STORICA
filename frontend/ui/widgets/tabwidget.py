from PyQt6.QtWidgets import QTabWidget, QTabBar, QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt


class StandardTabWidget(QTabWidget):
    """
    Standard reusable TabWidget with basic options
    
    Signals:
        tab_changed(int): Emitted when tab changes (index)
        tab_closed(int): Emitted when a tab is closed (index)
        tab_double_clicked(int): Emitted when tab is double-clicked (index)
    
    Usage:
        tabs = StandardTabWidget()
        tabs.add_tab(widget, "Tab Title")
        tabs.add_tab(widget, "Tab Title", closable=True)
        tabs.set_active_tab(0)
    """
    
    tab_changed = pyqtSignal(int)
    tab_closed = pyqtSignal(int)
    tab_double_clicked = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Basic configuration
        self.setMovable(True)
        self.setTabsClosable(False)
        self.setDocumentMode(False)
        
        # Connect signals
        self.currentChanged.connect(self._on_tab_changed)
        self.tabCloseRequested.connect(self._on_tab_close_requested)
        self.tabBarDoubleClicked.connect(self._on_tab_double_clicked)
        
        # Store tab data
        self._tab_data = {}  # index -> custom data
    
    def add_tab(self, widget: QWidget, title: str, closable: bool = False, 
                tooltip: str = "", data: any = None) -> int:
        """
        Add a new tab
        
        Args:
            widget: Widget to display in tab
            title: Tab title
            closable: Whether tab can be closed
            tooltip: Tooltip text for tab
            data: Custom data to store with tab
        
        Returns:
            int: Index of the new tab
        """
        index = self.addTab(widget, title)
        
        if tooltip:
            self.setTabToolTip(index, tooltip)
        
        if not hasattr(self, '_closable_tabs'):
            self._closable_tabs = set()

        if closable:
            self.setTabsClosable(True)
            self._closable_tabs.add(index)
        # Qt paints a close button on every tab once tabs are closable;
        # strip it from tabs that are not in `_closable_tabs`.
        self._sync_close_buttons()
        
        if data is not None:
            self._tab_data[index] = data
        
        return index
    
    def insert_tab(self, index: int, widget: QWidget, title: str, 
                   closable: bool = False, tooltip: str = "", data: any = None) -> int:
        """
        Insert a tab at specific position
        
        Args:
            index: Position to insert tab
            widget: Widget to display in tab
            title: Tab title
            closable: Whether tab can be closed
            tooltip: Tooltip text for tab
            data: Custom data to store with tab
        
        Returns:
            int: Index of the inserted tab
        """
        new_index = self.insertTab(index, widget, title)
        
        if tooltip:
            self.setTabToolTip(new_index, tooltip)
        
        if closable:
            self.setTabsClosable(True)
            if not hasattr(self, '_closable_tabs'):
                self._closable_tabs = set()
            self._closable_tabs.add(new_index)
        
        if data is not None:
            self._tab_data[new_index] = data
        
        return new_index
    
    def remove_tab(self, index: int):
        """
        Remove a tab at specified index
        
        Args:
            index: Index of tab to remove
        """
        widget = self.widget(index)
        if widget:
            widget.deleteLater()
        
        # Clean up stored data
        if index in self._tab_data:
            del self._tab_data[index]
        
        if hasattr(self, '_closable_tabs') and index in self._closable_tabs:
            self._closable_tabs.remove(index)
        
        self.removeTab(index)
        
        # Update stored indices for remaining tabs
        self._reindex_tab_data()
    
    def remove_current_tab(self):
        """Remove the currently active tab"""
        current_index = self.currentIndex()
        if current_index >= 0:
            self.remove_tab(current_index)
    
    def remove_all_tabs(self):
        """Remove all tabs"""
        while self.count() > 0:
            self.remove_tab(0)
    
    def set_tab_title(self, index: int, title: str):
        """
        Set tab title
        
        Args:
            index: Tab index
            title: New title
        """
        if 0 <= index < self.count():
            self.setTabText(index, title)
    
    def get_tab_title(self, index: int) -> str:
        """
        Get tab title
        
        Args:
            index: Tab index
        
        Returns:
            str: Tab title
        """
        if 0 <= index < self.count():
            return self.tabText(index)
        return ""
    
    def set_tab_tooltip(self, index: int, tooltip: str):
        """
        Set tab tooltip
        
        Args:
            index: Tab index
            tooltip: Tooltip text
        """
        if 0 <= index < self.count():
            self.setTabToolTip(index, tooltip)
    
    def set_tab_data(self, index: int, data: any):
        """
        Store custom data with tab
        
        Args:
            index: Tab index
            data: Custom data to store
        """
        if 0 <= index < self.count():
            self._tab_data[index] = data
    
    def get_tab_data(self, index: int) -> any:
        """
        Get custom data stored with tab
        
        Args:
            index: Tab index
        
        Returns:
            any: Custom data or None if not found
        """
        return self._tab_data.get(index)
    
    def get_current_tab_data(self) -> any:
        """Get custom data of current tab"""
        return self.get_tab_data(self.currentIndex())
    
    def set_tab_closable(self, index: int, closable: bool):
        """
        Set whether a tab can be closed
        
        Args:
            index: Tab index
            closable: True if tab can be closed
        """
        if 0 <= index < self.count():
            if closable:
                if not hasattr(self, '_closable_tabs'):
                    self._closable_tabs = set()
                self._closable_tabs.add(index)
                self.setTabsClosable(True)
            else:
                if hasattr(self, '_closable_tabs') and index in self._closable_tabs:
                    self._closable_tabs.remove(index)
                    if len(self._closable_tabs) == 0:
                        self.setTabsClosable(False)
    
    def is_tab_closable(self, index: int) -> bool:
        """
        Check if tab is closable
        
        Args:
            index: Tab index
        
        Returns:
            bool: True if tab can be closed
        """
        return (hasattr(self, '_closable_tabs') and 
                index in self._closable_tabs)
    
    def set_active_tab(self, index: int):
        """
        Set active tab by index
        
        Args:
            index: Tab index to activate
        """
        if 0 <= index < self.count():
            self.setCurrentIndex(index)
    
    def set_active_tab_by_widget(self, widget: QWidget):
        """
        Set active tab by widget reference
        
        Args:
            widget: Widget to activate
        """
        index = self.indexOf(widget)
        if index >= 0:
            self.setCurrentIndex(index)
    
    def get_current_widget(self) -> QWidget:
        """Get current tab's widget"""
        return self.currentWidget()
    
    def get_tab_widget(self, index: int) -> QWidget:
        """Get widget at tab index"""
        if 0 <= index < self.count():
            return self.widget(index)
        return None
    
    def get_tab_index_by_widget(self, widget: QWidget) -> int:
        """Get tab index by widget reference"""
        return self.indexOf(widget)
    
    def get_tab_index_by_data(self, data: any) -> int:
        """
        Find tab index by stored data
        
        Args:
            data: Data to search for
        
        Returns:
            int: Tab index or -1 if not found
        """
        for index, tab_data in self._tab_data.items():
            if tab_data == data:
                return index
        return -1
    
    def rename_current_tab(self, new_title: str):
        """Rename current tab"""
        self.set_tab_title(self.currentIndex(), new_title)
    
    def enable_tab_moving(self, enabled: bool = True):
        """Enable/disable tab moving"""
        self.setMovable(enabled)
    
    def enable_tabs_closable(self, enabled: bool = True):
        """Enable/disable all tabs being closable"""
        self.setTabsClosable(enabled)
        if not enabled:
            self._closable_tabs = set()
    
    def set_tab_position(self, position: str):
        """
        Set tab bar position
        
        Args:
            position: 'north', 'south', 'west', 'east'
        """
        positions = {
            'north': QTabWidget.TabPosition.North,
            'south': QTabWidget.TabPosition.South,
            'west': QTabWidget.TabPosition.West,
            'east': QTabWidget.TabPosition.East
        }
        if position.lower() in positions:
            self.setTabPosition(positions[position.lower()])
    
    def set_tab_shape(self, shape: str):
        """
        Set tab shape
        
        Args:
            shape: 'rounded' or 'triangular'
        """
        shapes = {
            'rounded': QTabWidget.TabShape.Rounded,
            'triangular': QTabWidget.TabShape.Triangular
        }
        if shape.lower() in shapes:
            self.setTabShape(shapes[shape.lower()])
    
    def set_document_mode(self, enabled: bool = True):
        """Enable/disable document mode"""
        self.setDocumentMode(enabled)
    
    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        self.tab_changed.emit(index)
    
    def _sync_close_buttons(self) -> None:
        """Show close buttons only on tabs marked closable."""
        if not hasattr(self, "_closable_tabs"):
            self._closable_tabs = set()
        bar = self.tabBar()
        for i in range(self.count()):
            if i in self._closable_tabs:
                continue
            bar.setTabButton(i, QTabBar.ButtonPosition.RightSide, None)

    def _on_tab_close_requested(self, index: int):
        """Handle tab close request"""
        if self.is_tab_closable(index):
            self.tab_closed.emit(index)
            self.remove_tab(index)
            self._sync_close_buttons()
    
    def _on_tab_double_clicked(self, index: int):
        """Handle tab double click"""
        if index >= 0:
            self.tab_double_clicked.emit(index)
    
    def _reindex_tab_data(self):
        """Reindex stored tab data after removal"""
        new_tab_data = {}
        new_index = 0
        
        for i in range(self.count()):
            if i in self._tab_data:
                new_tab_data[new_index] = self._tab_data[i]
            new_index += 1
        
        self._tab_data = new_tab_data
        
        # Reindex closable tabs
        if hasattr(self, '_closable_tabs'):
            new_closable = set()
            old_list = sorted(list(self._closable_tabs))
            for old_index in old_list:
                if old_index < self.count():
                    new_closable.add(old_index)
            self._closable_tabs = new_closable
    
    def get_tab_count(self) -> int:
        """Get number of tabs"""
        return self.count()
    
    def get_all_tabs_info(self) -> list:
        """
        Get information about all tabs
        
        Returns:
            list: List of dicts with tab info
        """
        tabs_info = []
        for i in range(self.count()):
            tabs_info.append({
                'index': i,
                'title': self.tabText(i),
                'tooltip': self.tabToolTip(i),
                'closable': self.is_tab_closable(i),
                'data': self.get_tab_data(i),
                'widget': self.widget(i)
            })
        return tabs_info