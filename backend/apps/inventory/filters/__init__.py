import django_filters

from apps.inventory.models import (
    Warehouse,
    Category,
    Product,
    Variant,
    Batch,
    StockMovement,
)


class WarehouseFilter(django_filters.FilterSet):
    class Meta:
        model = Warehouse
        fields = {
            "status": ["exact"],
            "is_active": ["exact"],
            "name": ["icontains"],
            "code": ["icontains"],
        }


class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        fields = {
            "parent": ["exact"],
            "is_active": ["exact"],
            "name": ["icontains"],
        }


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            "category": ["exact"],
            "unit": ["exact"],
            "is_active": ["exact"],
            "name": ["icontains"],
            "sku": ["icontains"],
        }


class VariantFilter(django_filters.FilterSet):
    class Meta:
        model = Variant
        fields = {
            "product": ["exact"],
            "is_active": ["exact"],
            "sku": ["icontains"],
            "name": ["icontains"],
        }


class BatchFilter(django_filters.FilterSet):
    class Meta:
        model = Batch
        fields = {
            "variant": ["exact"],
            "warehouse": ["exact"],
            "status": ["exact"],
            "is_active": ["exact"],
            "production_date": ["gte", "lte"],
            "expiry_date": ["gte", "lte"],
        }


class StockMovementFilter(django_filters.FilterSet):
    class Meta:
        model = StockMovement
        fields = {
            "movement_type": ["exact"],
            "status": ["exact"],
            "product": ["exact"],
            "batch": ["exact"],
            "from_warehouse": ["exact"],
            "to_warehouse": ["exact"],
            "movement_date": ["gte", "lte"],
        }
