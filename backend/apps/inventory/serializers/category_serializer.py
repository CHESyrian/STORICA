from typing import Any

from rest_framework import serializers

from common.exceptions.base import ValidationException

from apps.inventory.models import Category


# =========================================================
# CATEGORY LIST SERIALIZER
# =========================================================
class CategoryListSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(
        source="parent.name", read_only=True
    )

    class Meta:
        model = Category
        fields = [
            "id",
            "code",
            "slug",
            "name",
            "parent",
            "parent_name",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "slug",
            "parent_name",
            "created_at",
        ]


# =========================================================
# CATEGORY DETAIL SERIALIZER
# =========================================================
class CategoryDetailSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(
        source="parent.name", read_only=True
    )
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            "id",
            "code",
            "slug",
            "name",
            "description",
            "parent",
            "parent_name",
            "subcategories",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "slug",
            "parent_name",
            "subcategories",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]

    def get_subcategories(self, obj) -> list[dict[str, Any]]:
        return obj.subcategories.filter(is_active=True).values(
            "id", "name", "slug"
        )


# =========================================================
# CATEGORY CREATE SERIALIZER
# =========================================================
class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "name",
            "description",
            "parent",
        ]

    def validate_name(self, value):
        if not value.strip():
            raise ValidationException(
                message="Category name cannot be blank."
            )
        if Category.objects.filter(name=value.strip()).exists():
            raise ValidationException(
                message="A category with this name already exists."
            )
        return value.strip()

    def validate_parent(self, value):
        if value and not value.is_active:
            raise ValidationException(
                message="Cannot assign an inactive parent category."
            )
        return value


# =========================================================
# CATEGORY UPDATE SERIALIZER
# =========================================================
class CategoryUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "name",
            "description",
            "parent",
        ]

    def validate_name(self, value):
        if not value.strip():
            raise ValidationException(
                message="Category name cannot be blank."
            )
        qs = Category.objects.filter(
            name=value.strip()
        ).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationException(
                message="A category with this name already exists."
            )
        return value.strip()

    def validate_parent(self, value):
        if value:
            if not value.is_active:
                raise ValidationException(
                    message=(
                        "Cannot assign an inactive parent category."
                    )
                )
            if value.pk == self.instance.pk:
                raise ValidationException(
                    message="A category cannot be its own parent."
                )
        return value


# =========================================================
# CATEGORY DELETE SERIALIZER
# =========================================================
class CategoryDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
