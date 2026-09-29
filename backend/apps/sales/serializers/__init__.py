from .customer_serializer import (
    CustomerListSerializer,
    CustomerDetailSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer,
    CustomerDeleteSerializer,
)
from .sales_invoice_serializer import (
    SalesInvoiceListSerializer,
    SalesInvoiceDetailSerializer,
    SalesInvoiceCreateSerializer,
    SalesInvoiceUpdateSerializer,
    SalesInvoiceDeleteSerializer,
)
from .sales_invoice_item_serializer import (
    SalesInvoiceItemListSerializer,
    SalesInvoiceItemDetailSerializer,
    SalesInvoiceItemCreateSerializer,
    SalesInvoiceItemUpdateSerializer,
    SalesInvoiceItemDeleteSerializer,
)
from .sales_order_serializer import (
    SalesOrderListSerializer,
    SalesOrderDetailSerializer,
    SalesOrderCreateSerializer,
    SalesOrderUpdateSerializer,
    SalesOrderDeleteSerializer,
)
from .sales_order_item_serializer import (
    SalesOrderItemListSerializer,
    SalesOrderItemDetailSerializer,
    SalesOrderItemCreateSerializer,
    SalesOrderItemUpdateSerializer,
    SalesOrderItemDeleteSerializer,
)
from .sales_payment_serializer import (
    SalesPaymentListSerializer,
    SalesPaymentDetailSerializer,
    SalesPaymentCreateSerializer,
    SalesPaymentUpdateSerializer,
    SalesPaymentDeleteSerializer,
)


__all__ = [
    'CustomerListSerializer', 
    'CustomerDetailSerializer', 
    'CustomerCreateSerializer', 
    'CustomerUpdateSerializer', 
    'CustomerDeleteSerializer', 

    'SalesInvoiceListSerializer', 
    'SalesInvoiceDetailSerializer', 
    'SalesInvoiceCreateSerializer', 
    'SalesInvoiceUpdateSerializer', 
    'SalesInvoiceDeleteSerializer', 

    'SalesInvoiceItemListSerializer',
    'SalesInvoiceItemDetailSerializer',
    'SalesInvoiceItemCreateSerializer',
    'SalesInvoiceItemUpdateSerializer',
    'SalesInvoiceItemDeleteSerializer', 

    'SalesOrderListSerializer', 
    'SalesOrderDetailSerializer', 
    'SalesOrderCreateSerializer', 
    'SalesOrderUpdateSerializer', 
    'SalesOrderDeleteSerializer', 

    'SalesOrderItemListSerializer',
    'SalesOrderItemDetailSerializer',
    'SalesOrderItemCreateSerializer',
    'SalesOrderItemUpdateSerializer',
    'SalesOrderItemDeleteSerializer', 

    'SalesPaymentListSerializer', 
    'SalesPaymentDetailSerializer', 
    'SalesPaymentCreateSerializer', 
    'SalesPaymentUpdateSerializer', 
    'SalesPaymentDeleteSerializer', 
]

