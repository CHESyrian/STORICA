from rest_framework import serializers

from common.exceptions.base import ValidationException

from apps.purchases.models import PurchasesOrderItem


# =========================================================
# ORDER ITEM NESTED SERIALIZERS
# =========================================================
class PurchasesOrderItemNestedSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )
    class Meta:
        model = PurchasesOrderItem
        fields = [
            "id",
            "variant",
            "variant_name", 
            "quantity",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PurchasesOrderItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesOrderItem
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
# ORDER ITEM LIST SERIALIZER
# =========================================================
class PurchasesOrderItemListSerializer(serializers.ModelSerializer):
    order_code = serializers.CharField(
        source="order.code", read_only=True
    )
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = PurchasesOrderItem
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
# ORDER ITEM DETAIL SERIALIZER
# =========================================================
class PurchasesOrderItemDetailSerializer(serializers.ModelSerializer):
    order_code = serializers.CharField(
        source="order.code", read_only=True
    )
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = PurchasesOrderItem
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
# ORDER ITEM CREATE SERIALIZER
# =========================================================
class PurchasesOrderItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesOrderItem
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
        if PurchasesOrderItem.objects.filter(
            order=order, variant=variant
        ).exists():
            raise ValidationException(
                message=(
                    "This variant already exists in the order."
                )
            )
        return attrs


# =========================================================
# ORDER ITEM UPDATE SERIALIZER
# =========================================================
class PurchasesOrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesOrderItem
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
# ORDER ITEM DELETE SERIALIZER
# =========================================================
class PurchasesOrderItemDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value

