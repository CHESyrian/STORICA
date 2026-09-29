"""Serializers for aggregated stock status rows (not model-backed)."""
from rest_framework import serializers


class StockStatusSerializer(serializers.Serializer):
    """One row of on-hand stock: variant × warehouse."""

    variant = serializers.IntegerField()
    variant_sku = serializers.CharField()
    variant_name = serializers.CharField(allow_blank=True)
    product = serializers.IntegerField()
    product_name = serializers.CharField()
    product_sku = serializers.CharField()
    category = serializers.IntegerField(allow_null=True)
    category_name = serializers.CharField(allow_blank=True)
    warehouse = serializers.IntegerField()
    warehouse_name = serializers.CharField()
    warehouse_code = serializers.CharField()
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    min_stock = serializers.DecimalField(max_digits=12, decimal_places=2)
    is_low_stock = serializers.BooleanField()
    batch_count = serializers.IntegerField()
    earliest_expiry = serializers.DateField(allow_null=True)
    latest_production = serializers.DateField(allow_null=True)
    cost_value = serializers.DecimalField(max_digits=18, decimal_places=2)
