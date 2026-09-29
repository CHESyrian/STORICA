"""
UI Widgets for STORICA application.
"""

from .navbar import Navbar
from .toasts import Toast
from .paginated_table import PaginatedTableView
from .table import StandardTable
from .custom_messages import CustomMessageBox
from .custom_icons import color_icon
from .tabwidget import StandardTabWidget
from .loading_overlay import LoadingOverlay
from .modern_button import ModernButton, MsgModernButton
from .brand import BrandWidget
from .storica_main import StoricaWidget


__all__ = [
	"Navbar", 
	"Toast", 
	"PaginatedTableView", 
	"StandardTable", 
	"CustomMessageBox", 
	"color_icon", 
	"StandardTabWidget", 
	"LoadingOverlay", 
	"ModernButton", 
	"MsgModernButton", 
	"BrandWidget", 
	"StoricaWidget", 
]