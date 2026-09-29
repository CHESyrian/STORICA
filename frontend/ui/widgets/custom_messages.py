"""
Custom MessageBox with professional styling
Extends QMessageBox with STORICA branding
"""

from PyQt6.QtWidgets import QMessageBox, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

from frontend.utils.constants import Color


class CustomMessageBox(QMessageBox):
    """Custom styled message box for STORICA"""
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.setup_styling()
        
    def setup_styling(self):
        """Apply custom styling"""
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set minimum size
        self.setMinimumSize(400, 200)
        
        # Customize buttons
        for button in self.buttons():
            if button.text() == "OK":
                button.setProperty("default", True)
            elif button.text() == "Cancel":
                button.setProperty("secondary", True)
            elif button.text() == "Yes":
                button.setProperty("success", True)
            elif button.text() == "No":
                button.setProperty("danger", True)
    
    @classmethod
    def information(cls, parent: QWidget, title: str, text: str, 
                    buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok) -> int:
        """Show information message box"""
        msg = cls(parent)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(buttons)
        return msg.exec()
    
    @classmethod
    def warning(cls, parent: QWidget, title: str, text: str,
                buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok) -> int:
        """Show warning message box"""
        msg = cls(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(buttons)
        return msg.exec()
    
    @classmethod
    def critical(cls, parent: QWidget, title: str, text: str,
                 buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok) -> int:
        """Show critical error message box"""
        msg = cls(parent)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(buttons)
        return msg.exec()
    
    @classmethod
    def question(cls, parent: QWidget, title: str, text: str,
                 buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) -> int:
        """Show question message box"""
        msg = cls(parent)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(buttons)
        return msg.exec()