from rest_framework import serializers

from common.exceptions.base import ValidationException
from common.models.choices import OrderStatus

from apps.purchases.models import PurchasesOrder, PurchasesOrderItem

from .purchases_order_item_serializer import (
    PurchasesOrderItemNestedSerializer,
    PurchasesOrderItemWriteSerializer,
)


# =========================================================
# ORDER LIST SERIALIZER
# =========================================================
class PurchasesOrderListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.name", read_only=True
    )

    class Meta:
        model = PurchasesOrder
        fields = [
            "id",
            "code",
            "supplier",
            "supplier_name",
            "order_date",
            "status",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "supplier_name",
            "created_at",
        ]


# =========================================================
# ORDER DETAIL SERIALIZER
# =========================================================
class PurchasesOrderDetailSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.name", read_only=True
    )
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True
    )
    updated_by_name = serializers.CharField(
        source="updated_by.username", read_only=True
    )
    items = PurchasesOrderItemNestedSerializer(many=True, read_only=True)

    class Meta:
        model = PurchasesOrder
        fields = [
            "id",
            "code",
            "supplier",
            "supplier_name",
            "order_date",
            "status",
            "is_active",
            "notes",
            "items",
            "created_by",
            "created_by_name", 
            "updated_by",
            "updated_by_name", 
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "supplier_name",
            "items",
            "created_by",
            "created_by_name", 
            "updated_by",
            "updated_by_name", 
            "created_at",
            "updated_at",
        ]


# =========================================================
# ORDER CREATE SERIALIZER
# =========================================================
class PurchasesOrderCreateSerializer(serializers.ModelSerializer):
    items = PurchasesOrderItemWriteSerializer(many=True)

    class Meta:
        model = PurchasesOrder
        fields = [
            "supplier",
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
                message="Duplicate variants are not allowed in the same order."
            )
        return value


# =========================================================
# ORDER UPDATE SERIALIZER
# =========================================================
class PurchasesOrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesOrder
        fields = [
            "supplier",
            "order_date",
            "status",
            "notes",
        ]

    def validate_status(self, value):
        instance = self.instance
        if instance and instance.status == OrderStatus.CANCELLED.value:
            raise ValidationException(
                message="Cannot update a cancelled order."
            )
        return value


# =========================================================
# ORDER DELETE SERIALIZER
# =========================================================
class PurchasesOrderDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
