"""
ui/dialogs/__init__.py

UI Dialogs for STORICA application.

Usage
-----
    from ui.dialogs import AddProductDialog, AddVariantDialog
"""
from .show_data_dialog import ShowDataDialog
# Inventory Dialogs
from .inventory_dialogs.category_dialog import AddCategoryDialog
from .inventory_dialogs.warehouse_dialog import AddWarehouseDialog
from .inventory_dialogs.product_dialog import AddProductDialog
from .inventory_dialogs.variant_dialog import AddVariantDialog
from .inventory_dialogs.batch_dialog import AddBatchDialog
from .inventory_dialogs.stock_movement_dialog import AddStockMovementDialog

# Purchases Dialogs
from .purchases_dialogs.supplier_dialog import AddSupplierDialog
from .purchases_dialogs.purchase_order_dialog import (
    AddPurchaseOrderDialog, 
)
from .purchases_dialogs.purchase_invoice_dialog import (
    AddPurchaseInvoiceDialog, 
)
from .purchases_dialogs.purchase_payment_dialog import (
    AddPurchasePaymentDialog
)

# Sales Dialogs
from .sales_dialogs.customer_dialog import AddCustomerDialog
from .sales_dialogs.sales_order_dialog import (
    AddSalesOrderDialog, 
)
from .sales_dialogs.sales_invoice_dialog import (
    AddSalesInvoiceDialog
)
from .sales_dialogs.sales_payment_dialog import AddSalesPaymentDialog

from .users_dialogs.user_dialog import (
    AddUserDialog, EditUserDialog, ProfileDialog,
    ChangePasswordDialog, ResetPasswordDialog,
)

__all__ = [
    "ShowDataDialog", 
    
    # Inventory Dialogs
    "AddCategoryDialog",
    "AddWarehouseDialog",
    "AddProductDialog",
    "AddVariantDialog",
    "AddBatchDialog",
    "AddStockMovementDialog",

    # Purchases Dialogs
    "AddSupplierDialog", 
    "AddPurchaseOrderDialog", 
    "AddPurchaseInvoiceDialog", 
    "AddPurchasePaymentDialog", 
    "ViewPurchaseOrderDialog", 
    "ViewPurchaseInvoiceDialog", 

    # Sales Dialogs
    "AddCustomerDialog", 
    "AddSalesOrderDialog", 
    "AddSalesInvoiceDialog",
    "AddSalesPaymentDialog",
    "AddUserDialog",
    "EditUserDialog",
    "ProfileDialog",
    "ChangePasswordDialog",
    "ResetPasswordDialog",
]

