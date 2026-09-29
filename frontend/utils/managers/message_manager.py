"""
Centralized message and dialog manager for STORICA
Professional message handling with custom styling and toast notifications
"""
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QSizePolicy, 
    QTextEdit, QLabel, QPushButton, QFrame, QApplication, 
    QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve, QTimer
)
from PyQt6.QtGui import (
    QFont, QIcon, QColor, QPalette, QFontDatabase, 
    QTextOption
)

from frontend.ui.widgets import MsgModernButton
from frontend.utils.constants import (
    StatusMessage, MessageType, COLORS_STYLE
)

from .toast_manager import ToastManager


class MessageDialog(QDialog):
    """Modern, professional message dialog with animations and custom styling"""
    
    def __init__(
        self,
        title: str,
        message: str,
        message_type: MessageType = MessageType.INFO,
        informative_text: str = "",
        parent: Optional[QWidget] = None,
        modal: bool = True
    ):
        super().__init__(parent)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(modal)
        
        self.message_type = message_type
        self.result_value = -1
        self.drag_position = None
        
        self._setup_ui(title, message, informative_text)
        self._setup_animation()
        self._center_on_parent()
        
    def _setup_ui(self, title: str, message: str, informative_text: str):
        """Setup the modern UI with dark theme"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Main container with shadow effect - DARK THEME
        container = QFrame(self)
        container.setObjectName("msgDialogContainer")
        
        # Shadow effect (simulated with border)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 28, 32, 28)
        container_layout.setSpacing(16)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(self.message_type.value[0])
        icon_label.setObjectName("msgIconLabel")
        icon_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(48, 48)
        # Set icon color based on message type
        icon_label.setProperty("messageType", self.message_type.name.lower())
        header_layout.addWidget(icon_label)
        
        # Title - DARK THEME
        title_label = QLabel(title)
        title_label.setObjectName("msgTitleLabel")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Close button (X) - DARK THEME
        close_btn = QPushButton("✕")
        close_btn.setObjectName("msgCloseButton")
        close_btn.setFixedSize(36, 36)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        
        container_layout.addLayout(header_layout)
        
        # Separator - DARK THEME
        separator = QFrame()
        separator.setObjectName("msgSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)
        container_layout.addWidget(separator)
        
        # Message - DARK THEME
        message_edit = QTextEdit()
        message_edit.setObjectName("msgMessageEdit")
        message_edit.setReadOnly(True)
        message_edit.setFrameShape(QFrame.Shape.NoFrame)
        message_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        message_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        message_edit.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        message_edit.setText(message)
        message_edit.setFont(QFont("Segoe UI", 12))
        message_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        container_layout.addWidget(message_edit)
        
        # Informative text - DARK THEME
        if informative_text:
            info_label = QLabel(informative_text)
            info_label.setObjectName("msgInfoLabel")
            info_label.setFont(QFont("Segoe UI", 11))
            info_label.setWordWrap(True)
            container_layout.addWidget(info_label)
                
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()
        
        self._button_container = button_layout
        container_layout.addLayout(button_layout)
        
        main_layout.addWidget(container)
        
        # Set size based on content
        self.setMinimumWidth(540)
        self.setMinimumHeight(180)
        self.adjustSize()
    
    def _setup_buttons(self, *buttons):
        """Add buttons to the dialog"""
        # Clear existing buttons
        while self._button_container.count():
            item = self._button_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for btn_config in buttons:
            text, btn_type, role = btn_config
            button = MsgModernButton(text, btn_type)
            # Store role in button for later retrieval
            button.setProperty("role", role)
            button.clicked.connect(lambda checked, r=role: self._handle_result(r))
            self._button_container.addWidget(button)
        
        self._button_container.addStretch()
        
    def _handle_result(self, result):
        """Handle button click result"""
        self.result_value = result
        if result == QDialog.DialogCode.Accepted:
            self.accept()
        elif result == QDialog.DialogCode.Rejected:
            self.reject()
        else:
            # Custom result (e.g., -1, 0, 1)
            self.done(result)
    
    def _setup_animation(self):
        """Apply entrance animation using opacity effect"""
        # Use opacity effect for fade-in
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.opacity_effect.setOpacity(0)
        self.setGraphicsEffect(self.opacity_effect)
        
        # Create animation
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.start()
        
        # Add a slight scale effect using geometry animation
        self._original_geometry = self.geometry()
        self._scale_animation = QPropertyAnimation(self, b"geometry")
        self._scale_animation.setDuration(200)
        self._scale_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Start slightly smaller and grow to full size
        start_geo = self._original_geometry
        start_geo.setWidth(int(start_geo.width() * 0.95))
        start_geo.setHeight(int(start_geo.height() * 0.95))
        start_geo.moveCenter(self._original_geometry.center())
        
        self._scale_animation.setStartValue(start_geo)
        self._scale_animation.setEndValue(self._original_geometry)
        self._scale_animation.start()
        
    def _center_on_parent(self):
        """Center dialog on parent window"""
        if self.parent():
            parent_geo = self.parent().geometry()
            self.move(
                parent_geo.center().x() - self.width() // 2,
                parent_geo.center().y() - self.height() // 2
            )
        else:
            # Center on screen
            screen = QApplication.primaryScreen().geometry()
            self.move(
                screen.center().x() - self.width() // 2,
                screen.center().y() - self.height() // 2
            )
    
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        self.drag_position = None
        event.accept()
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            # Find the default button and click it
            for button in self.findChildren(MsgModernButton):
                if button.isDefault():
                    button.click()
                    return
        super().keyPressEvent(event)
    
    # Static methods for different dialog types
    @classmethod
    def info(
        cls,
        title: str,
        message: str,
        informative_text: str = "",
        parent: Optional[QWidget] = None
    ) -> bool:
        """Show info dialog"""
        dialog = cls(title, message, MessageType.INFO, informative_text, parent)
        dialog._setup_buttons(("OK", "primary", QDialog.DialogCode.Accepted))
        return dialog.exec() == QDialog.DialogCode.Accepted
    
    @classmethod
    def success(
        cls,
        title: str,
        message: str,
        informative_text: str = "Operation completed successfully.",
        parent: Optional[QWidget] = None
    ) -> bool:
        """Show success dialog"""
        dialog = cls(title, message, MessageType.SUCCESS, informative_text, parent)
        dialog._setup_buttons(("OK", "success", QDialog.DialogCode.Accepted))
        # Make OK button default
        ok_button = dialog.findChildren(MsgModernButton)[0] if dialog.findChildren(MsgModernButton) else None
        if ok_button:
            ok_button.setDefault(True)
        return dialog.exec() == QDialog.DialogCode.Accepted
    
    @classmethod
    def warning(
        cls,
        title: str,
        message: str,
        informative_text: str = "",
        parent: Optional[QWidget] = None
    ) -> bool:
        """Show warning dialog"""
        dialog = cls(title, message, MessageType.WARNING, informative_text, parent)
        dialog._setup_buttons(("OK", "secondary", QDialog.DialogCode.Accepted))
        return dialog.exec() == QDialog.DialogCode.Accepted
    
    @classmethod
    def error(
        cls,
        title: str,
        message: str,
        informative_text: str = "Please contact support if the issue persists.",
        parent: Optional[QWidget] = None
    ) -> bool:
        """Show error dialog"""
        dialog = cls(title, message, MessageType.ERROR, informative_text, parent)
        dialog._setup_buttons(("OK", "danger", QDialog.DialogCode.Accepted))
        return dialog.exec() == QDialog.DialogCode.Accepted
    
    @classmethod
    def question(
        cls,
        title: str,
        message: str,
        informative_text: str = "",
        parent: Optional[QWidget] = None,
        default_no: bool = False
    ) -> bool:
        """Show question dialog with Yes/No buttons"""
        dialog = cls(title, message, MessageType.QUESTION, informative_text, parent)
        dialog._setup_buttons(
            ("No", "secondary", QDialog.DialogCode.Rejected),
            ("Yes", "primary", QDialog.DialogCode.Accepted)
        )
        # Set default button
        buttons = dialog.findChildren(MsgModernButton)
        if buttons:
            if default_no and len(buttons) > 1:
                buttons[0].setDefault(True)  # No button
            else:
                buttons[-1].setDefault(True)  # Yes button
        return dialog.exec() == QDialog.DialogCode.Accepted
    
    @classmethod
    def yes_no_cancel(
        cls,
        title: str,
        message: str,
        informative_text: str = "",
        parent: Optional[QWidget] = None
    ) -> int:
        """Show dialog with Yes/No/Cancel options"""
        dialog = cls(title, message, MessageType.QUESTION, informative_text, parent)
        dialog._setup_buttons(
            ("Cancel", "secondary", -1),
            ("No", "danger", 0),
            ("Yes", "success", 1)
        )
        # Set Yes as default
        buttons = dialog.findChildren(MsgModernButton)
        if buttons:
            buttons[-1].setDefault(True)  # Yes button
        result = dialog.exec()
        return dialog.result_value if hasattr(dialog, 'result_value') else -1


# ------------------------------------------------------------------
# MessageManager
# ------------------------------------------------------------------
class MessageManager:
    """Centralized manager for all message dialogs with professional 
        styling and toast notifications"""
    
    _instance = None
    
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
        self.toast_manager = ToastManager()
    
    @staticmethod
    def _get_parent(parent: Optional[QWidget] = None) -> Optional[QWidget]:
        """Get parent widget"""
        return parent
    
    def set_toast_parent(self, parent: QWidget):
        """Set the parent widget for toast notifications"""
        self.toast_manager.set_parent(parent)
    
    # Toast notification methods
    def toast_info(
        self, 
        message: str, 
        duration: int = 5000, 
        parent: Optional[QWidget] = None
    ):
        """Show an info toast notification"""
        self.toast_manager.show_toast(message, "info", duration, parent)
    
    def toast_success(
        self, 
        message: str, 
        duration: int = 5000, 
        parent: Optional[QWidget] = None
    ):
        """Show a success toast notification"""
        self.toast_manager.show_toast(message, "success", duration, parent)
    
    def toast_warning(
        self, 
        message: str, 
        duration: int = 5000, 
        parent: Optional[QWidget] = None
    ):
        """Show a warning toast notification"""
        self.toast_manager.show_toast(message, "warning", duration, parent)
    
    def toast_error(
        self, 
        message: str, 
        duration: int = 5000, 
        parent: Optional[QWidget] = None
    ):
        """Show an error toast notification (longer duration)"""
        self.toast_manager.show_toast(message, "error", duration, parent)
    
    # Dialog methods using new MessageDialog
    @classmethod
    def info(cls, title: str, message: str, parent: Optional[QWidget] = None):
        """Show professional information message"""
        MessageDialog.info(title, message, parent=cls._get_parent(parent))
    
    @classmethod
    def warning(cls, title: str, message: str, parent: Optional[QWidget] = None):
        """Show professional warning message"""
        MessageDialog.warning(title, message, parent=cls._get_parent(parent))
    
    @classmethod
    def error(cls, title: str, message: str, parent: Optional[QWidget] = None):
        """Show professional error message"""
        MessageDialog.error(title, message, parent=cls._get_parent(parent))
    
    @classmethod
    def question(
        cls, 
        title: str, 
        message: str, 
        parent: Optional[QWidget] = None,
        default_no: bool = False
    ) -> bool:
        """Ask a professional question dialog"""
        return MessageDialog.question(
            title, message, parent=cls._get_parent(parent), default_no=default_no
        )
    
    @classmethod
    def yes_no_cancel(
        cls, 
        title: str, 
        message: str, 
        parent: Optional[QWidget] = None
    ) -> int:
        """Show professional Yes/No/Cancel dialog"""
        return MessageDialog.yes_no_cancel(title, message, parent=cls._get_parent(parent))
    
    @classmethod
    def delete_confirmation(
        cls, 
        item_name: str, 
        parent: Optional[QWidget] = None
    ) -> bool:
        """Show professional delete confirmation dialog"""
        return cls.question(
            "Confirm Deletion",
            f"Are you sure you want to delete '{item_name}'?",
            parent,
            default_no=True
        )
    
    @classmethod
    def logout_confirmation(cls, parent: Optional[QWidget] = None) -> bool:
        """Show professional logout confirmation dialog"""
        return cls.question(
            "Confirm Logout",
            "Are you sure you want to end the current session?",
            parent,
            default_no=True
        )
    
    @classmethod
    def save_confirmation(cls, parent: Optional[QWidget] = None) -> int:
        """Show professional save confirmation dialog"""
        return cls.yes_no_cancel(
            "Unsaved Changes",
            "Do you want to save your changes before closing?",
            parent
        )
    
    @classmethod
    def success(cls, title: str, message: str, parent: Optional[QWidget] = None):
        """Show professional success message"""
        MessageDialog.success(title, message, parent=cls._get_parent(parent))
    
    @classmethod
    def connection_error(cls, parent: Optional[QWidget] = None):
        """Show professional connection error message"""
        MessageDialog.error(
            "Connection Error",
            "Unable to connect to the server.",
            "Please check your network connection and try again.",
            cls._get_parent(parent)
        )
    
    @classmethod
    def operation_success(
        cls, 
        operation: str, 
        item_name: str = "", 
        parent: Optional[QWidget] = None
    ):
        """Show professional operation success message"""
        message = f"{operation} completed successfully"
        if item_name:
            message = f"{item_name} has been {operation.lower()}d successfully"
        cls.success("Success", message, parent)
    
    @classmethod
    def operation_error(
        cls, 
        operation: str, 
        error: str, 
        parent: Optional[QWidget] = None
    ):
        """Show professional operation error message"""
        MessageDialog.error(
            f"{operation} Failed",
            f"Unable to {operation.lower()} the operation.",
            f"Error: {error}\n\nPlease try again or contact support if the issue persists.",
            cls._get_parent(parent)
        )
    
    @classmethod
    def show_status_message(
        cls, 
        message_type: str, 
        title: str, 
        message: str, 
        parent: Optional[QWidget] = None
    ):
        """Show message based on status type"""
        if message_type == StatusMessage.SUCCESS:
            cls.success(title, message, parent)

        elif message_type == StatusMessage.ERROR:
            cls.error(title, message, parent)

        elif message_type == StatusMessage.INFO:
            cls.info(title, message, parent)

        else:
            cls.info(title, message, parent)
    
    # Show toast based on status type
    def show_status_toast(
        self, 
        message_type: str, 
        message: str, 
        parent: Optional[QWidget] = None,
        duration: int = 3000
    ):
        """Show toast notification based on status type"""
        if message_type == StatusMessage.SUCCESS:
            self.toast_success(message, duration, parent)

        elif message_type == StatusMessage.ERROR:
            self.toast_error(message, duration, parent)

        elif message_type == StatusMessage.INFO:
            self.toast_info(message, duration, parent)

        else:
            self.toast_info(message, duration, parent)