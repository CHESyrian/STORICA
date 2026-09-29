from rest_framework.routers import DefaultRouter


# ================================================
# Default API Router
# ================================================
api_router = DefaultRouter()


# ================================================
# USERS URLS
# ================================================
from apps.users.views import (
    AuthViewSet
)

# Register Auth ViewSet (optional, you can keep JWT views separate)
api_router.register(
    prefix=r'auth',
    viewset=AuthViewSet,
    basename='auth'
)


# ================================================
# INVENTORY URLS
# ================================================
from apps.inventory.views import (
    BatchViewSet,
    CategoryViewSet,
    ProductViewSet,
    StockMovementViewSet,
    StockStatusViewSet,
    VariantViewSet,
    WarehouseViewSet,
)


api_router.register(
    prefix="warehouses",
    viewset=WarehouseViewSet,
    basename="warehouse",
)

api_router.register(
    prefix="categories",
    viewset=CategoryViewSet,
    basename="category",
)

api_router.register(
    prefix="products",
    viewset=ProductViewSet,
    basename="product",
)

api_router.register(
    prefix="variants",
    viewset=VariantViewSet,
    basename="variant",
)

api_router.register(
    prefix="batches",
    viewset=BatchViewSet,
    basename="batch",
)

api_router.register(
    prefix="stock-movements",
    viewset=StockMovementViewSet,
    basename="stock_movement",
)

api_router.register(
    prefix="stock-status",
    viewset=StockStatusViewSet,
    basename="stock_status",
)



# ================================================
# SALES URLS
# ================================================
from apps.sales.views import (
    CustomerViewSet, 
    SalesOrderViewSet, 
    SalesOrderItemViewSet, 
    SalesInvoiceViewSet,
    SalesInvoiceItemViewSet,
    SalesPaymentViewSet,
)


api_router.register(
    r"customers",
    CustomerViewSet,
    basename="customer",
)

api_router.register(
    r"sales-orders",
    SalesOrderViewSet,
    basename="sales_order",
)

api_router.register(
    r"sales-order-items",
    SalesOrderItemViewSet,
    basename="sales_order_item",
)

api_router.register(
    r"sales-invoices",
    SalesInvoiceViewSet,
    basename="sales_invoice",
)

api_router.register(
    r"sales-invoice-items",
    SalesInvoiceItemViewSet,
    basename="sales_invoice_item",
)

api_router.register(
    r"sales-payments",
    SalesPaymentViewSet,
    basename="sales_payment",
)



# ================================================
# PURCHASES URLS
# ================================================
from apps.purchases.views import (
    SupplierViewSet, 
    PurchasesOrderViewSet,
    PurchasesOrderItemViewSet, 
    PurchasesInvoiceViewSet, 
    PurchasesInvoiceItemViewSet, 
    PurchasesPaymentViewSet, 
)


api_router.register(
    r"suppliers",
    SupplierViewSet,
    basename="supplier",
)

api_router.register(
    r"purchases-orders",
    PurchasesOrderViewSet,
    basename="purchases_order",
)

api_router.register(
    r"purchases-order-items",
    PurchasesOrderItemViewSet,
    basename="purchases_order_item",
)

api_router.register(
    r"purchases-invoices",
    PurchasesInvoiceViewSet,
    basename="purchases_invoice",
)

api_router.register(
    r"purchases-invoice-items",
    PurchasesInvoiceItemViewSet,
    basename="purchases_invoice_item",
)

api_router.register(
    r"purchases-payments",
    PurchasesPaymentViewSet,
    basename="purchases_payment",
)



# ================================================
# ACCOUNTING URLS
# ================================================
from apps.accounting.views import AccountingReportViewSet

api_router.register(
    r"accounting",
    AccountingReportViewSet,
    basename="accounting",
)


