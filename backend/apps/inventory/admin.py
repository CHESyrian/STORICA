from django.contrib import admin

from apps.inventory.models import (
    Warehouse,
    Category,
    Product,
    Variant,
    Batch,
    StockMovement,
)


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "status", "phone", "is_active", "created_at")
    list_filter = ("status", "is_active")
    search_fields = ("code", "name", "phone")
    readonly_fields = ("code", "created_at", "updated_at")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "parent", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    readonly_fields = ("code", "created_at", "updated_at")
    raw_id_fields = ("parent",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "category", "unit", "is_active", "created_at")
    list_filter = ("unit", "is_active", "category")
    search_fields = ("sku", "name")
    readonly_fields = ("sku", "created_at", "updated_at")
    raw_id_fields = ("category",)


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "product", "quantity", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("sku", "name", "product__name")
    readonly_fields = ("sku", "quantity", "created_at", "updated_at")
    raw_id_fields = ("product",)


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "variant",
        "warehouse",
        "quantity",
        "cost_price",
        "status",
        "production_date",
        "expiry_date",
        "is_active",
    )
    list_filter = ("status", "is_active", "warehouse")
    search_fields = ("code", "variant__sku", "variant__name")
    readonly_fields = ("code", "created_at", "updated_at")
    raw_id_fields = ("variant", "warehouse")
    date_hierarchy = "production_date"


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = (
        "movement_id",
        "movement_type",
        "status",
        "product",
        "batch",
        "quantity",
        "from_warehouse",
        "to_warehouse",
        "reference_number",
        "movement_date",
    )
    list_filter = ("movement_type", "status")
    search_fields = ("reference_number", "product__sku", "product__name")
    readonly_fields = ("movement_id", "completed_at")
    raw_id_fields = (
        "product",
        "batch",
        "from_warehouse",
        "to_warehouse",
        "performed_by",
        "approved_by",
        "created_by",
    )
    date_hierarchy = "movement_date"
