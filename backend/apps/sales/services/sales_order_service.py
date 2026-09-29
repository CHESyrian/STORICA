from django.db import transaction

from common.generators import GenCodeEngine
from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
)
from common.models.choices import OrderStatus

from apps.sales.models import SalesOrder, SalesOrderItem


# =========================================================
# SALES ORDER SERVICE
# =========================================================
class SalesOrderService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(order_id: int) -> SalesOrder:
        try:
            return (
                SalesOrder.objects
                .select_related("customer")
                .prefetch_related("items__variant")
                .get(pk=order_id)
            )
        except SalesOrder.DoesNotExist:
            raise NotFoundException(
                message=f"Order with id {order_id} not found."
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user=None) -> SalesOrder:
        items_data = validated_data.pop("items")

        order = SalesOrder(
            customer=validated_data["customer"],
            notes=validated_data.get("notes", ""),
            status=OrderStatus.DRAFT.value,
        )
        if validated_data.get("order_date") is not None:
            order.order_date = validated_data["order_date"]

        order.code = GenCodeEngine.sales_order(SalesOrder)

        if user:
            order.created_by = user
            order.updated_by = user

        order.save()

        SalesOrderService._create_items(order, items_data)

        return order

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        order_id: int,
        validated_data: dict,
        user=None,
        partial: bool = False,
    ) -> SalesOrder:
        order = SalesOrder.objects.select_for_update().get(
            pk=order_id
        )

        if order.status == OrderStatus.CANCELLED.value:
            raise BusinessLogicException(
                message="Cannot update a cancelled order."
            )

        fields = ["customer", "order_date", "status", "notes"]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(order, field, validated_data[field])

        if user:
            order.updated_by = user

        order.save()
        return order

    # --------------------------------------------------
    # CONFIRM (draft → confirmed)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def confirm(order_id: int, user=None) -> SalesOrder:
        order = SalesOrder.objects.select_for_update().get(
            pk=order_id
        )

        if order.status != OrderStatus.DRAFT.value:
            raise BusinessLogicException(
                message=(
                    f"Cannot confirm an order with status "
                    f"'{order.status}'. Only draft orders "
                    f"can be confirmed."
                )
            )

        if not order.items.exists():
            raise BusinessLogicException(
                message="Cannot confirm an order with no line items."
            )

        order.status = OrderStatus.CONFIRMED.value
        if user:
            order.updated_by = user
        order.save()
        return order

    # --------------------------------------------------
    # COMPLETE (processing/shipped/delivered → completed)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def complete(order_id: int, user=None) -> SalesOrder:
        order = SalesOrder.objects.select_for_update().get(
            pk=order_id
        )

        allowed = {
            OrderStatus.PROCESSING.value,
            OrderStatus.SHIPPED.value,
            OrderStatus.DELIVERED.value,
        }
        if order.status not in allowed:
            raise BusinessLogicException(
                message=(
                    f"Cannot complete an order with status "
                    f"'{order.status}'. Order must be processing, "
                    f"shipped, or delivered."
                )
            )

        order.status = OrderStatus.COMPLETED.value
        if user:
            order.updated_by = user
        order.save()
        return order

    # --------------------------------------------------
    # CANCEL
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def cancel(order_id: int, user=None) -> SalesOrder:
        order = SalesOrder.objects.select_for_update().get(
            pk=order_id
        )

        if not order.can_cancel():
            raise BusinessLogicException(
                message=(
                    f"Cannot cancel an order with status "
                    f"'{order.status}'."
                )
            )

        order.status = OrderStatus.CANCELLED.value

        if user:
            order.updated_by = user

        order.save()
        return order

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(order_id: int, user=None) -> None:
        order = SalesOrder.objects.select_for_update().get(
            pk=order_id
        )

        if order.status not in {
            OrderStatus.DRAFT.value,
            OrderStatus.CANCELLED.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Only draft or cancelled orders can be deleted."
                )
            )

        order.soft_delete(deleted_by=user)

    # --------------------------------------------------
    # INTERNAL HELPERS
    # --------------------------------------------------
    @staticmethod
    def _create_items(
        order: SalesOrder,
        items_data: list,
    ) -> None:
        items = [
            SalesOrderItem(
                order=order,
                variant=item["variant"],
                quantity=item["quantity"],
            )
            for item in items_data
        ]
        SalesOrderItem.objects.bulk_create(items)
