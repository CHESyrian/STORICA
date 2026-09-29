from django.db import transaction

from common.generators import GenCodeEngine
from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
)

from apps.inventory.models import Product


# =========================================================
# PRODUCT SERVICE
# =========================================================
class ProductService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(product_id: int) -> Product:
        try:
            return (
                Product.objects
                .select_related("category")
                .get(pk=product_id)
            )
        except Product.DoesNotExist:
            raise NotFoundException(
                message=f"Product with id {product_id} not found."
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user=None) -> Product:
        product = Product(
            name=validated_data["name"],
            description=validated_data.get("description", ""),
            category=validated_data["category"],
            unit=validated_data.get("unit", "pcs"),
            image=validated_data.get("image"),
            notes=validated_data.get("notes", ""),
        )

        product.sku = GenCodeEngine.sku(Product)

        if user:
            product.created_by = user
            product.updated_by = user

        product.save()
        return product

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        product_id: int,
        validated_data: dict,
        user=None,
        partial: bool = False,
    ) -> Product:
        product = Product.objects.select_for_update().get(
            pk=product_id
        )

        fields = [
            "name",
            "description",
            "category",
            "unit",
            "image",
            "notes",
        ]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(product, field, validated_data[field])

        if user:
            product.updated_by = user

        product.save()
        return product

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(product_id: int, user=None) -> None:
        product = Product.objects.select_for_update().get(
            pk=product_id
        )

        if product.variants.filter(is_active=True).exists():
            raise BusinessLogicException(
                message=(
                    "Cannot deactivate a product that has "
                    "active variants."
                )
            )

        product.soft_delete(deleted_by=user)
