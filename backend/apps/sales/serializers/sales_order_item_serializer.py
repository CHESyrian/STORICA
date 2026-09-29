from rest_framework import serializers

from common.exceptions.base import ValidationException

from apps.sales.models import SalesOrderItem


# =========================================================
# SALES ORDER ITEM LIST SERIALIZER
# =========================================================
class SalesOrderItemListSerializer(serializers.ModelSerializer):
    order_code = serializers.CharField(
        source="order.code", read_only=True
    )
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = SalesOrderItem
        fields = [
            "id",
            "order",
            "order_code",
            "variant",
            "variant_name",
            "quantity",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "order_code",
            "variant_name",
            "created_at",
        ]


# =========================================================
# SALES ORDER ITEM DETAIL SERIALIZER
# =========================================================
class SalesOrderItemDetailSerializer(serializers.ModelSerializer):
    order_code = serializers.CharField(
        source="order.code", read_only=True
    )
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = SalesOrderItem
        fields = [
            "id",
            "order",
            "order_code",
            "variant",
            "variant_name",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "order_code",
            "variant_name",
            "created_at",
            "updated_at",
        ]


# =========================================================
# SALES ORDER ITEM CREATE SERIALIZER
# =========================================================
class SalesOrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderItem
        fields = [
            "order",
            "variant",
            "quantity",
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise ValidationException(
                message="Quantity must be at least 1."
            )
        return value

    def validate(self, attrs):
        order = attrs.get("order")
        variant = attrs.get("variant")
        if SalesOrderItem.objects.filter(
            order=order, variant=variant
        ).exists():
            raise ValidationException(
                message="This variant already exists in the order."
            )
        return attrs


# =========================================================
# SALES ORDER ITEM UPDATE SERIALIZER
# =========================================================
class SalesOrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderItem
        fields = [
            "quantity",
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise ValidationException(
                message="Quantity must be at least 1."
            )
        return value


# =========================================================
# SALES ORDER ITEM DELETE SERIALIZER
# =========================================================
class SalesOrderItemDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
