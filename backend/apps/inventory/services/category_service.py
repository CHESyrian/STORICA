from django.db import transaction

from common.generators import GenCodeEngine
from common.exceptions.base import (
    NotFoundException,
    ConflictException,
    BusinessLogicException,
    ValidationException,
)

from apps.inventory.models import Category


# =========================================================
# CATEGORY SERVICE
# =========================================================
class CategoryService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(category_id: int) -> Category:
        try:
            return (
                Category.objects
                .select_related("parent")
                .prefetch_related("subcategories")
                .get(pk=category_id)
            )
        except Category.DoesNotExist:
            raise NotFoundException(
                message=(
                    f"Category with id {category_id} not found."
                )
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user=None) -> Category:
        name = validated_data["name"]

        if Category.objects.filter(name=name).exists():
            raise ConflictException(
                message="A category with this name already exists."
            )

        category = Category(
            name=name,
            description=validated_data.get("description", ""),
            parent=validated_data.get("parent"),
        )

        category.code = GenCodeEngine.category(Category)

        if user:
            category.created_by = user
            category.updated_by = user

        category.save()
        return category

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        category_id: int,
        validated_data: dict,
        user=None,
        partial: bool = False,
    ) -> Category:
        category = Category.objects.select_for_update().get(
            pk=category_id
        )

        parent = validated_data.get("parent")
        if parent and parent.pk == category_id:
            raise ValidationException(
                message="A category cannot be its own parent."
            )

        fields = ["name", "description", "parent"]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(category, field, validated_data[field])

        if user:
            category.updated_by = user

        category.save()
        return category

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(category_id: int, user=None) -> None:
        category = Category.objects.select_for_update().get(
            pk=category_id
        )

        if category.products.filter(is_active=True).exists():
            raise BusinessLogicException(
                message=(
                    "Cannot deactivate a category that has "
                    "active products."
                )
            )

        if category.subcategories.filter(is_active=True).exists():
            raise BusinessLogicException(
                message=(
                    "Cannot deactivate a category that has "
                    "active subcategories."
                )
            )

        category.soft_delete(deleted_by=user)
