"""
Toast Manager
Manages multiple toast notifications with queue system
"""
from typing import Optional
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint

from frontend.ui.widgets.toasts import Toast


class ToastManager:
    """Manages toast notifications with queue system"""
    
    _instance = None
    MAX_VISIBLE_TOASTS = 3
    TOAST_SPACING = 10
    
    def __new__(cls):
        """Singleton pattern to ensure single instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.active_toasts = []
        self.parent_widget = None
        
    def set_parent(self, parent: QWidget):
        """Set the parent widget for toasts"""
        self.parent_widget = parent
        
    def show_toast(
        self,
        message: str,
        toast_type: str = "info",
        duration: int = 3000,
        parent: Optional[QWidget] = None
    ):
        """Show a toast notification"""
        parent_widget = parent or self.parent_widget
        
        if not parent_widget:
            # Fallback: use any top-level widget
            parent_widget = QApplication.activeWindow()
            
        if not parent_widget:
            print(f"Warning: Cannot show toast - no parent widget: {message}")
            return
            
        # Create toast
        toast = Toast(message, parent_widget, toast_type, duration)
        
        # Position the toast
        self.position_toast(toast)
        
        # Show toast
        toast.show()
        self.active_toasts.append(toast)
        
        # Clean up when toast is closed
        toast.destroyed.connect(lambda: self.remove_toast(toast))
        
        # Limit visible toasts
        if len(self.active_toasts) > self.MAX_VISIBLE_TOASTS:
            oldest = self.active_toasts[0]
            oldest.close_toast()
            
    def position_toast(self, toast: Toast):
        """Position toast at the bottom right of parent"""
        if not toast.parent():
            return
            
        # Force geometry update to get correct dimensions
        toast.adjustSize()
        
        # Calculate position from bottom
        parent_rect = toast.parent().rect()
        toast_width = toast.width() if toast.width() > 0 else 320
        toast_height = toast.height() if toast.height() > 0 else 60
        
        # Position from bottom-right
        x = parent_rect.width() - toast_width - 20
        y = parent_rect.height() - toast_height - 20
        
        # Adjust for existing toasts
        offset = 0
        for active_toast in self.active_toasts:
            if active_toast != toast and active_toast.isVisible():
                offset += active_toast.height() + self.TOAST_SPACING
                
        y -= offset
        
        # Ensure within bounds
        y = max(10, y)
        
        toast.move(x, y)
        
    def remove_toast(self, toast: Toast):
        """Remove toast from active list"""
        if toast in self.active_toasts:
            self.active_toasts.remove(toast)
            
        # Reposition remaining toasts
        self.reposition_all_toasts()
        
    def reposition_all_toasts(self):
        """Reposition all active toasts"""
        offset = 0
        for toast in reversed(self.active_toasts):
            if toast.isVisible():
                parent_rect = toast.parent().rect()
                toast_width = toast.width()
                toast_height = toast.height()
                
                x = parent_rect.width() - toast_width - 20
                y = parent_rect.height() - toast_height - 20 - offset
                
                # Animate movement
                anim = QPropertyAnimation(toast, b"pos")
                anim.setDuration(200)
                anim.setEndValue(QPoint(x, y))
                anim.setEasingCurve(QEasingCurve.Type.OutCubic)
                anim.start()
                
                offset += toast_height + self.TOAST_SPACING