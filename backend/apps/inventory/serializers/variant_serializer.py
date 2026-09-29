from decimal import Decimal

from rest_framework import serializers

from common.exceptions.base import ValidationException

from apps.inventory.models import Variant


# =========================================================
# VARIANT LIST SERIALIZER
# =========================================================
class VariantListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name", read_only=True
    )
    product_sku = serializers.CharField(
        source="product.sku", read_only=True
    )

    class Meta:
        model = Variant
        fields = [
            "id",
            "sku",
            "slug",
            "product",
            "product_name",
            "product_sku",
            "name",
            "quantity",
            "min_stock",
            "color",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "sku",
            "slug",
            "product_name",
            "product_sku",
            "created_at",
        ]


# =========================================================
# VARIANT DETAIL SERIALIZER
# =========================================================
class VariantDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name", read_only=True
    )
    product_sku = serializers.CharField(
        source="product.sku", read_only=True
    )

    class Meta:
        model = Variant
        fields = [
            "id",
            "sku",
            "slug",
            "product",
            "product_name",
            "product_sku",
            "name",
            "quantity",
            "min_stock",
            "color",
            "weight",
            "length",
            "width",
            "height",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "sku",
            "slug",
            "product_name",
            "product_sku",
            "quantity",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


# =========================================================
# VARIANT CREATE SERIALIZER
# =========================================================
class VariantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = [
            "product",
            "name",
            "color",
            "weight",
            "length",
            "width",
            "height",
            "min_stock",
        ]

    def validate_product(self, value):
        if not value.is_active:
            raise ValidationException(
                message="Cannot create a variant for an inactive product."
            )
        return value

    def validate_weight(self, value):
        if value is not None and value <= Decimal("0"):
            raise ValidationException(
                message="Weight must be greater than 0."
            )
        return value

    def validate_length(self, value):
        if value is not None and value <= Decimal("0"):
            raise ValidationException(
                message="Length must be greater than 0."
            )
        return value

    def validate_width(self, value):
        if value is not None and value <= Decimal("0"):
            raise ValidationException(
                message="Width must be greater than 0."
            )
        return value

    def validate_height(self, value):
        if value is not None and value <= Decimal("0"):
            raise ValidationException(
                message="Height must be greater than 0."
            )
        return value

    def validate_min_stock(self, value):
        if value is not None and value < Decimal("0"):
            raise ValidationException(
                message="Min stock cannot be negative."
            )
        return value


# =========================================================
# VARIANT UPDATE SERIALIZER
# =========================================================
class VariantUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = [
            "name",
            "color",
            "weight",
            "length",
            "width",
            "height",
            "min_stock",
        ]

    def validate_weight(self, value):
        if value is not None and value <= Decimal("0"):
            raise ValidationException(
                message="Weight must be greater than 0."
            )
        return value

    def validate_length(self, value):
        if value is not None and value <= Decimal("0"):
            raise ValidationException(
                message="Length must be greater than 0."
            )
        return value

    def validate_width(self, value):
        if value is not None and value <= Decimal("0"):
            raise ValidationException(
                message="Width must be greater than 0."
            )
        return value

    def validate_height(self, value):
        if value is not None and value <= Decimal("0"):
            raise ValidationException(
                message="Height must be greater than 0."
            )
        return value


    def validate_min_stock(self, value):
        if value is not None and value < Decimal("0"):
            raise ValidationException(
                message="Min stock cannot be negative."
            )
        return value


# =========================================================
# VARIANT DELETE SERIALIZER
# =========================================================
class VariantDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
