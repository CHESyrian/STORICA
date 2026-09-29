from django.db import transaction

from common.generators import GenCodeEngine
from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
)

from apps.inventory.models import Variant


# =========================================================
# VARIANT SERVICE
# =========================================================
class VariantService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(variant_id: int) -> Variant:
        try:
            return (
                Variant.objects
                .select_related("product")
                .get(pk=variant_id)
            )
        except Variant.DoesNotExist:
            raise NotFoundException(
                message=f"Variant with id {variant_id} not found."
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user=None) -> Variant:
        variant = Variant(
            product=validated_data["product"],
            name=validated_data.get("name", ""),
            color=validated_data.get("color"),
            weight=validated_data.get("weight"),
            length=validated_data.get("length"),
            width=validated_data.get("width"),
            height=validated_data.get("height"),
            min_stock=validated_data.get("min_stock", 0),
            quantity=0,
        )

        variant.sku = GenCodeEngine.sku(Variant)

        if user:
            variant.created_by = user
            variant.updated_by = user

        variant.save()
        return variant

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        variant_id: int,
        validated_data: dict,
        user=None,
        partial: bool = False,
    ) -> Variant:
        variant = Variant.objects.select_for_update().get(
            pk=variant_id
        )

        fields = [
            "name",
            "color",
            "weight",
            "length",
            "width",
            "height",
            "min_stock",
        ]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(variant, field, validated_data[field])

        if user:
            variant.updated_by = user

        variant.save()
        return variant

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(variant_id: int, user=None) -> None:
        variant = Variant.objects.select_for_update().get(
            pk=variant_id
        )

        if variant.quantity > 0:
            raise BusinessLogicException(
                message=(
                    "Cannot deactivate a variant with stock "
                    "quantity greater than 0."
                )
            )

        if variant.batches.filter(
            status__in=["active"]
        ).exists():
            raise BusinessLogicException(
                message=(
                    "Cannot deactivate a variant that has "
                    "active batches."
                )
            )

        variant.soft_delete(deleted_by=user)
