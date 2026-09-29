from django.db import transaction

from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
    ConflictException,
)
from common.models.choices import OrderStatus

from apps.purchases.models import PurchasesOrderItem


# =========================================================
# PURCHASES ORDER ITEM SERVICE
# =========================================================
class PurchasesOrderItemService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(item_id: int) -> PurchasesOrderItem:
        try:
            return (
                PurchasesOrderItem.objects
                .select_related("order", "variant")
                .get(pk=item_id)
            )
        except PurchasesOrderItem.DoesNotExist:
            raise NotFoundException(
                message=f"Order item with id {item_id} not found."
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict) -> PurchasesOrderItem:
        order = validated_data["order"]
        variant = validated_data["variant"]

        if order.status not in {
            OrderStatus.DRAFT.value,
            OrderStatus.CONFIRMED.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Items can only be added to draft or "
                    "confirmed orders."
                )
            )

        if PurchasesOrderItem.objects.filter(
            order=order, variant=variant
        ).exists():
            raise ConflictException(
                message="This variant already exists in the order."
            )

        item = PurchasesOrderItem.objects.create(
            order=order,
            variant=variant,
            quantity=validated_data["quantity"],
        )
        return item

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        item_id: int,
        validated_data: dict,
        partial: bool = False,
    ) -> PurchasesOrderItem:
        item = PurchasesOrderItem.objects.select_for_update().get(
            pk=item_id
        )

        if item.order.status not in {
            OrderStatus.DRAFT.value,
            OrderStatus.CONFIRMED.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Items can only be updated on draft or "
                    "confirmed orders."
                )
            )

        if "quantity" in validated_data:
            item.quantity = validated_data["quantity"]

        item.save()
        return item

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(item_id: int) -> None:
        item = PurchasesOrderItem.objects.select_for_update().get(
            pk=item_id
        )

        if item.order.status not in {
            OrderStatus.DRAFT.value,
            OrderStatus.CONFIRMED.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Items can only be removed from draft or "
                    "confirmed orders."
                )
            )

        item.delete()
