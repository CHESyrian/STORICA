import django_filters

from apps.purchases.models import (
    Supplier,
    PurchasesOrder,
    PurchasesInvoice,
    PurchasesPayment,
)


class SupplierFilter(django_filters.FilterSet):
    class Meta:
        model = Supplier
        fields = {
            "is_verified": ["exact"],
            "is_active": ["exact"],
            "name": ["icontains"],
            "email": ["icontains"],
        }


class PurchasesOrderFilter(django_filters.FilterSet):
    class Meta:
        model = PurchasesOrder
        fields = {
            "status": ["exact"],
            "supplier": ["exact"],
            "is_active": ["exact"],
            "order_date": ["gte", "lte"],
        }


class PurchasesInvoiceFilter(django_filters.FilterSet):
    class Meta:
        model = PurchasesInvoice
        fields = {
            "status": ["exact"],
            "supplier": ["exact"],
            "order": ["exact"],
            "warehouse": ["exact"],
            "is_active": ["exact"],
            "invoice_date": ["gte", "lte"],
        }


class PurchasesPaymentFilter(django_filters.FilterSet):
    class Meta:
        model = PurchasesPayment
        fields = {
            "status": ["exact"],
            "invoice": ["exact"],
            "supplier": ["exact"],
            "payment_date": ["gte", "lte"],
        }
