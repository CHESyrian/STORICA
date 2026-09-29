"""
UI Tabs for STORICA application.
"""
from .panel.panel_tab import PanelTab
from .panel.report_tab import ReportTab
# Inventory
from .inventory.product_tab import ProductTab
from .inventory.variant_tab import VariantTab
from .inventory.category_tab import CategoryTab
from .inventory.warehouse_tab import WarehouseTab
from .inventory.batch_tab import BatchTab
from .inventory.stock_movement_tab import StockMovementTab
from .inventory.stock_status_tab import StockStatusTab

# Purchases
from .purchases.orders_tab import PurchasesOrderTab
from .purchases.invoices_tab import PurchasesInvoiceTab
from .purchases.payments_tab import PaymentsTab
from .purchases.suppliers_tab import SuppliersTab

# Sales
from .sales.orders_tab import SalesOrderTab
from .sales.invoices_tab import SalesInvoiceTab
from .sales.customers_tab import CustomersTab
from .sales.payments_tab import SalesPaymentsTab


__all__ = [
	# Panel
	"PanelTab",
	"ReportTab",

	# Inventory
	"ProductTab", 
	"VariantTab", 
	"CategoryTab", 
	"WarehouseTab", 
	"BatchTab",
	"StockMovementTab",
	"StockStatusTab",

	# Purchases
	"PurchasesOrderTab", 
	"PurchasesInvoiceTab", 
	"PaymentsTab", 
	"SuppliersTab", 

	# Sales
	"SalesOrderTab", 
	"SalesInvoiceTab", 
	"CustomersTab",
	"SalesPaymentsTab",
]