from .customer_view import (
    CustomerViewSet,
)
from .sales_invoice_view import (
    SalesInvoiceViewSet,
)
from .sales_invoice_item_view import (
    SalesInvoiceItemViewSet,
)
from .sales_order_view import (
    SalesOrderViewSet,
)
from .sales_order_item_view import (
    SalesOrderItemViewSet,
)
from .sales_payment_view import (
    SalesPaymentViewSet,
)


__all__ = [
    'CustomerViewSet', 
    'SalesInvoiceViewSet', 
    'SalesInvoiceItemViewSet', 
    'SalesOrderViewSet', 
    'SalesOrderItemViewSet', 
    'SalesPaymentViewSet', 
]

