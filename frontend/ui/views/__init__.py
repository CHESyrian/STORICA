"""
UI Views for STORICA application.
"""

from .inventory_view import InventoryView
from .purchases_view import PurchasesView
from .sales_view import SalesView
from .panel_view import PanelView
from .users_view import UsersView


__all__ = [
	"InventoryView", 
	"PurchasesView", 
	"SalesView", 
	"PanelView",
	"UsersView"
]