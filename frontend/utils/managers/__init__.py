"""
Manager for STORICA application.
"""

from frontend.utils.managers.auth_manager import AuthManager
from frontend.utils.managers.message_manager import MessageManager
from frontend.utils.managers.theme_manager import ThemeManager
from frontend.utils.managers.logging_manager import LoggingManager


__all__ = [
	"AuthManager", 
	"MessageManager", 
	"ThemeManager", 
	"LoggingManager"
]