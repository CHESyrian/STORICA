# frontend/controllers/__init__.py

# Panel
from .panel.panel_controller import PanelController

# Inventory
from .inventory.category_controller import CategoryController
from .inventory.product_controller import ProductController
from .inventory.stock_movement_controller import StockMovementController
from .inventory.variant_controller import VariantController
from .inventory.warehouse_controller import WarehouseController
from .inventory.batch_controller import BatchController
from .inventory.stock_status_controller import StockStatusController

# Purchases
from .purchases.purchases_controller import PurchasesController
from .purchases.purchase_invoice_controller import PurchaseInvoiceController
from .purchases.purchase_invoice_item_controller import PurchaseInvoiceItemController
from .purchases.purchase_order_controller import PurchaseOrderController
from .purchases.purchase_order_item_controller import PurchaseOrderItemController
from .purchases.purchase_payment_controller import PurchasePaymentController
from .purchases.supplier_controller import SupplierController

# Sales
from .sales.sales_controller import SalesController
from .sales.customer_controller import CustomerController
from .sales.sales_invoice_controller import SalesInvoiceController
from .sales.sales_invoice_item_controller import SalesInvoiceItemController
from .sales.sales_order_controller import SalesOrderController
from .sales.sales_order_item_controller import SalesOrderItemController
from .sales.sales_payment_controller import SalesPaymentController

from .users.user_controller import UserController

__all__ = [
    "PanelController",
    
    # Inventory
    "CategoryController",
    "ProductController",
    "StockMovementController",
    "VariantController",
    "WarehouseController",
    "BatchController",
    "StockStatusController",

    # Purchases
    "PurchasesController", 
    "PurchaseInvoiceController",
    "PurchaseInvoiceItemController",
    "PurchaseOrderController",
    "PurchaseOrderItemController",
    "PurchasePaymentController",
    "SupplierController",

     # Sales
    "SalesController",
    "SalesInvoiceController",
    "SalesInvoiceItemController",
    "SalesOrderController",
    "SalesOrderItemController",
    "SalesPaymentController",
    "UserController", 
    "CustomerController", 
]