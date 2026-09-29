import django_filters

from apps.sales.models import (
    Customer,
    SalesOrder,
    SalesInvoice,
    SalesPayment,
)


class CustomerFilter(django_filters.FilterSet):
    class Meta:
        model = Customer
        fields = {
            "is_verified": ["exact"],
            "is_active": ["exact"],
            "name": ["icontains"],
            "email": ["icontains"],
        }


class SalesOrderFilter(django_filters.FilterSet):
    class Meta:
        model = SalesOrder
        fields = {
            "status": ["exact"],
            "customer": ["exact"],
            "is_active": ["exact"],
            "order_date": ["gte", "lte"],
        }


class SalesInvoiceFilter(django_filters.FilterSet):
    class Meta:
        model = SalesInvoice
        fields = {
            "status": ["exact"],
            "customer": ["exact"],
            "order": ["exact"],
            "is_active": ["exact"],
            "invoice_date": ["gte", "lte"],
        }


class SalesPaymentFilter(django_filters.FilterSet):
    class Meta:
        model = SalesPayment
        fields = {
            "status": ["exact"],
            "invoice": ["exact"],
            "customer": ["exact"],
            "payment_date": ["gte", "lte"],
        }
