from rest_framework import serializers

from common.exceptions.base import ValidationException
from common.models.choices import OrderStatus

from apps.sales.models import SalesOrder, SalesOrderItem


# =========================================================
# ORDER ITEM NESTED SERIALIZERS
# =========================================================
class SalesOrderItemNestedSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = SalesOrderItem
        fields = [
            "id",
            "variant",
            "variant_name",
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "variant_name",
            "created_at",
            "updated_at",
        ]


class SalesOrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrderItem
        fields = [
            "variant",
            "quantity",
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise ValidationException(
                message="Quantity must be at least 1."
            )
        return value


# =========================================================
# SALES ORDER LIST SERIALIZER
# =========================================================
class SalesOrderListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name", read_only=True
    )

    class Meta:
        model = SalesOrder
        fields = [
            "id",
            "code",
            "customer",
            "customer_name",
            "order_date",
            "status",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "customer_name",
            "created_at",
        ]


# =========================================================
# SALES ORDER DETAIL SERIALIZER
# =========================================================
class SalesOrderDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name", read_only=True
    )
    items = SalesOrderItemNestedSerializer(many=True, read_only=True)

    class Meta:
        model = SalesOrder
        fields = [
            "id",
            "code",
            "customer",
            "customer_name",
            "order_date",
            "status",
            "is_active",
            "notes",
            "items",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "customer_name",
            "items",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


# =========================================================
# SALES ORDER CREATE SERIALIZER
# =========================================================
class SalesOrderCreateSerializer(serializers.ModelSerializer):
    items = SalesOrderItemWriteSerializer(many=True)

    class Meta:
        model = SalesOrder
        fields = [
            "customer",
            "order_date",
            "notes",
            "items",
        ]

    def validate_items(self, value):
        if not value:
            raise ValidationException(
                message="Order must have at least one item."
            )
        variant_ids = [item["variant"].pk for item in value]
        if len(variant_ids) != len(set(variant_ids)):
            raise ValidationException(
                message=(
                    "Duplicate variants are not allowed "
                    "in the same order."
                )
            )
        return value


# =========================================================
# SALES ORDER UPDATE SERIALIZER
# =========================================================
class SalesOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrder
        fields = [
            "customer",
            "order_date",
            "status",
            "notes",
        ]

    def validate_status(self, value):
        instance = self.instance
        if (
            instance
            and instance.status == OrderStatus.CANCELLED.value
        ):
            raise ValidationException(
                message="Cannot update a cancelled order."
            )
        return value


# =========================================================
# SALES ORDER DELETE SERIALIZER
# =========================================================
class SalesOrderDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
