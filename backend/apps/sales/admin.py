from django.contrib import admin

from apps.sales.models import (
    Customer,
    SalesOrder,
    SalesOrderItem,
    SalesInvoice,
    SalesInvoiceItem,
    SalesPayment,
)


class SalesOrderItemInline(admin.TabularInline):
    model = SalesOrderItem
    extra = 0
    raw_id_fields = ("variant",)


class SalesInvoiceItemInline(admin.TabularInline):
    model = SalesInvoiceItem
    extra = 0
    raw_id_fields = ("variant",)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name", "email", "phone", "is_verified", "is_active", "created_at"
    )
    list_filter = ("is_verified", "is_active")
    search_fields = ("code", "name", "email", "phone")
    readonly_fields = ("code", "created_at", "updated_at")


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("code", "customer", "status", "order_date", "is_active")
    list_filter = ("status", "is_active")
    search_fields = ("code", "customer__name")
    readonly_fields = ("code", "created_at", "updated_at")
    raw_id_fields = ("customer",)
    inlines = [SalesOrderItemInline]
    date_hierarchy = "order_date"


@admin.register(SalesInvoice)
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "customer",
        "order",
        "status",
        "total_amount",
        "amount_paid",
        "invoice_date",
        "is_active",
    )
    list_filter = ("status", "is_active")
    search_fields = ("code", "customer__name")
    readonly_fields = ("code", "created_at", "updated_at")
    raw_id_fields = ("customer", "order")
    inlines = [SalesInvoiceItemInline]
    date_hierarchy = "invoice_date"


@admin.register(SalesPayment)
class SalesPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "payment_id",
        "transaction_id",
        "invoice",
        "customer",
        "amount",
        "status",
        "payment_date",
    )
    list_filter = ("status",)
    search_fields = ("transaction_id", "invoice__code", "customer__name")
    raw_id_fields = ("invoice", "order", "customer", "processed_by")
    date_hierarchy = "payment_date"
