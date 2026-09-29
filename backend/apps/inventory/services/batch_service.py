from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from common.generators import GenCodeEngine
from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
)
from common.models.choices import BatchStatus

from apps.inventory.models import Batch, Variant, Warehouse


# =========================================================
# BATCH SERVICE
# =========================================================
class BatchService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(batch_id: int) -> Batch:
        try:
            return (
                Batch.objects
                .select_related("variant__product", "warehouse")
                .get(pk=batch_id)
            )
        except Batch.DoesNotExist:
            raise NotFoundException(
                message=f"Batch with id {batch_id} not found."
            )

    # --------------------------------------------------
    # FIFO ALLOCATION
    # --------------------------------------------------
    @staticmethod
    def allocate_fifo(
        variant: Variant,
        quantity: Decimal,
        warehouse: Warehouse | None = None,
    ) -> list[tuple[Batch, Decimal]]:
        """
        Allocate ``quantity`` from active batches for ``variant``
        using FIFO (oldest production_date, then earliest id).

        Optionally restrict to a single warehouse.

        Returns a list of (batch, qty_from_batch) that sums to
        ``quantity``. Raises BusinessLogicException if stock is
        insufficient.

        **Transaction / locking contract**

        - Must be called inside an open ``transaction.atomic`` block.
          This method issues ``SELECT … FOR UPDATE`` on candidate
          batches; without an outer transaction those locks are
          released immediately and concurrent posts can oversell.
        - Returned ``Batch`` instances are already row-locked for the
          duration of the current transaction. Prefer mutating via
          those instances (or re-fetch with ``select_for_update``)
          before saving quantity changes.
        - Do not call from request handlers or serializers directly;
          keep usage inside inventory / sales / purchases services.
        """
        if quantity <= 0:
            raise BusinessLogicException(
                message="Allocation quantity must be positive."
            )

        qs = (
            Batch.objects
            .select_for_update()
            .filter(
                variant=variant,
                status=BatchStatus.ACTIVE,
                is_active=True,
                quantity__gt=0,
            )
            .order_by("production_date", "id")
        )
        if warehouse is not None:
            qs = qs.filter(warehouse=warehouse)

        remaining = quantity
        allocations: list[tuple[Batch, Decimal]] = []

        for batch in qs:
            if remaining <= 0:
                break
            take = min(batch.quantity, remaining)
            if take > 0:
                allocations.append((batch, take))
                remaining -= take

        if remaining > 0:
            available = quantity - remaining
            raise BusinessLogicException(
                message=(
                    f"Insufficient stock for variant "
                    f"'{variant.sku}'. Available: {available}, "
                    f"requested: {quantity}."
                )
            )

        return allocations

    # --------------------------------------------------
    # FIND OR CREATE TARGET BATCH (for transfers)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def get_or_create_target_batch(
        *,
        source_batch: Batch,
        to_warehouse: Warehouse,
        user=None,
    ) -> Batch:
        """
        Find an active batch for the same variant in ``to_warehouse``
        with the same cost/production/expiry profile, or create one
        with quantity 0 (caller will increase quantity).
        """
        existing = (
            Batch.objects
            .select_for_update()
            .filter(
                variant=source_batch.variant,
                warehouse=to_warehouse,
                status=BatchStatus.ACTIVE,
                is_active=True,
                cost_price=source_batch.cost_price,
                production_date=source_batch.production_date,
                expiry_date=source_batch.expiry_date,
            )
            .order_by("id")
            .first()
        )
        if existing:
            return existing

        batch = Batch(
            variant=source_batch.variant,
            warehouse=to_warehouse,
            quantity=Decimal("0"),
            cost_price=source_batch.cost_price,
            production_date=source_batch.production_date,
            expiry_date=source_batch.expiry_date,
            status=BatchStatus.ACTIVE,
        )
        batch.code = GenCodeEngine.batch(Batch)
        if user:
            batch.created_by = user
            batch.updated_by = user
        batch.save()
        return batch

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user=None) -> Batch:
        variant: Variant = (
            Variant.objects
            .select_for_update()
            .get(pk=validated_data["variant"].pk)
        )

        batch = Batch(
            variant=variant,
            warehouse=validated_data["warehouse"],
            quantity=validated_data["quantity"],
            cost_price=validated_data["cost_price"],
            production_date=validated_data["production_date"],
            expiry_date=validated_data.get("expiry_date"),
            status=validated_data.get(
                "status", BatchStatus.ACTIVE
            ),
        )

        batch.code = GenCodeEngine.batch(Batch)

        if user:
            batch.created_by = user
            batch.updated_by = user

        batch.save()

        # Update variant stock quantity
        variant.quantity += validated_data["quantity"]
        variant.save()

        return batch

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        batch_id: int,
        validated_data: dict,
        user=None,
        partial: bool = False,
    ) -> Batch:
        batch = Batch.objects.select_for_update().get(pk=batch_id)

        if batch.status == BatchStatus.RECALLED:
            raise BusinessLogicException(
                message="Cannot update a recalled batch."
            )

        old_quantity = batch.quantity
        new_quantity = validated_data.get("quantity", old_quantity)

        fields = [
            "quantity",
            "cost_price",
            "production_date",
            "expiry_date",
            "status",
        ]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(batch, field, validated_data[field])

        if user:
            batch.updated_by = user

        batch.save()

        # Adjust variant quantity if batch quantity changed
        if new_quantity != old_quantity:
            if new_quantity < 0:
                raise BusinessLogicException(
                    message="Batch quantity cannot be negative."
                )
            variant = Variant.objects.select_for_update().get(
                pk=batch.variant.pk
            )
            variant.quantity += new_quantity - old_quantity
            if variant.quantity < 0:
                raise BusinessLogicException(
                    message=(
                        "Updating batch quantity would make variant "
                        f"stock negative ({variant.quantity})."
                    )
                )
            variant.save()

        return batch

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(batch_id: int, user=None) -> None:
        batch = Batch.objects.select_for_update().get(pk=batch_id)

        if batch.status == BatchStatus.ACTIVE and batch.quantity > 0:
            raise BusinessLogicException(
                message=(
                    "Cannot deactivate an active batch with "
                    "remaining quantity."
                )
            )

        batch.soft_delete(deleted_by=user)
