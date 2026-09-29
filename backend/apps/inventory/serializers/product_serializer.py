from rest_framework import serializers

from common.exceptions.base import ValidationException
from common.models.choices import UnitChoices

from apps.inventory.models import Product


# =========================================================
# PRODUCT LIST SERIALIZER
# =========================================================
class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name", read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "slug",
            "name",
            "category",
            "category_name",
            "unit",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "sku",
            "slug",
            "category_name",
            "created_at",
        ]


# =========================================================
# PRODUCT DETAIL SERIALIZER
# =========================================================
class ProductDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source="category.name", read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "slug",
            "name",
            "description",
            "category",
            "category_name",
            "unit",
            "image",
            "notes",
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
            "category_name",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


# =========================================================
# PRODUCT CREATE SERIALIZER
# =========================================================
class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "category",
            "unit",
            "image",
            "notes",
        ]

    def validate_name(self, value):
        if not value.strip():
            raise ValidationException(
                message="Product name cannot be blank."
            )
        return value.strip()

    def validate_category(self, value):
        if not value.is_active:
            raise ValidationException(
                message="Cannot assign an inactive category."
            )
        return value

    def validate_unit(self, value):
        valid = [choice[0] for choice in UnitChoices.choices]
        if value not in valid:
            raise ValidationException(
                message=f"Invalid unit. Choices: {valid}."
            )
        return value


# =========================================================
# PRODUCT UPDATE SERIALIZER
# =========================================================
class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "category",
            "unit",
            "image",
            "notes",
        ]

    def validate_name(self, value):
        if not value.strip():
            raise ValidationException(
                message="Product name cannot be blank."
            )
        return value.strip()

    def validate_category(self, value):
        if not value.is_active:
            raise ValidationException(
                message="Cannot assign an inactive category."
            )
        return value

    def validate_unit(self, value):
        valid = [choice[0] for choice in UnitChoices.choices]
        if value not in valid:
            raise ValidationException(
                message=f"Invalid unit. Choices: {valid}."
            )
        return value


# =========================================================
# PRODUCT DELETE SERIALIZER
# =========================================================
class ProductDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
