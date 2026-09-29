from django.contrib import admin

from apps.purchases.models import (
    Supplier,
    PurchasesOrder,
    PurchasesOrderItem,
    PurchasesInvoice,
    PurchasesInvoiceItem,
    PurchasesPayment,
)


class PurchasesOrderItemInline(admin.TabularInline):
    model = PurchasesOrderItem
    extra = 0
    raw_id_fields = ("variant",)


class PurchasesInvoiceItemInline(admin.TabularInline):
    model = PurchasesInvoiceItem
    extra = 0
    raw_id_fields = ("variant",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "code", "name", "email", "phone", "is_verified", "is_active", "created_at"
    )
    list_filter = ("is_verified", "is_active")
    search_fields = ("code", "name", "email", "phone")
    readonly_fields = ("code", "created_at", "updated_at")


@admin.register(PurchasesOrder)
class PurchasesOrderAdmin(admin.ModelAdmin):
    list_display = ("code", "supplier", "status", "order_date", "is_active")
    list_filter = ("status", "is_active")
    search_fields = ("code", "supplier__name")
    readonly_fields = ("code", "created_at", "updated_at")
    raw_id_fields = ("supplier",)
    inlines = [PurchasesOrderItemInline]
    date_hierarchy = "order_date"


@admin.register(PurchasesInvoice)
class PurchasesInvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "supplier",
        "order",
        "warehouse",
        "status",
        "total_amount",
        "amount_paid",
        "invoice_date",
        "is_active",
    )
    list_filter = ("status", "is_active")
    search_fields = ("code", "supplier__name")
    readonly_fields = ("code", "created_at", "updated_at")
    raw_id_fields = ("supplier", "order", "warehouse")
    inlines = [PurchasesInvoiceItemInline]
    date_hierarchy = "invoice_date"


@admin.register(PurchasesPayment)
class PurchasesPaymentAdmin(admin.ModelAdmin):
    list_display = (
        "payment_id",
        "transaction_id",
        "invoice",
        "supplier",
        "amount",
        "status",
        "payment_date",
    )
    list_filter = ("status",)
    search_fields = ("transaction_id", "invoice__code", "supplier__name")
    raw_id_fields = ("invoice", "order", "supplier", "processed_by")
    date_hierarchy = "payment_date"
