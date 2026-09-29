from django.db import transaction
from django.db.models import Sum as models_sum
from django.utils import timezone

from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
)
from common.models.choices import (
    StockMovementType,
    MovementStatus,
)

from apps.inventory.models import StockMovement, Variant, Batch


# =========================================================
# STOCK MOVEMENT SERVICE
# =========================================================
class StockMovementService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(movement_id: int) -> StockMovement:
        try:
            return (
                StockMovement.objects
                .select_related(
                    "product",
                    "batch",
                    "from_warehouse",
                    "to_warehouse",
                    "performed_by",
                    "approved_by",
                    "created_by",
                )
                .get(pk=movement_id)
            )
        except StockMovement.DoesNotExist:
            raise NotFoundException(
                message=(
                    f"Stock movement with id {movement_id} "
                    f"not found."
                )
            )

    # --------------------------------------------------
    # CREATE (normal path — PENDING)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(
        validated_data: dict,
        user=None,
    ) -> StockMovement:
        """
        Create a stock movement in PENDING status.

        Quantity changes are applied only when the movement is later
        transitioned to COMPLETED via `update()` (see `_apply_stock_change`).

        For cases where the caller has already mutated batch/variant
        quantities (e.g. purchase-invoice receiving via BatchService),
        use `record_purchase_receipt` instead so stock is not double-counted.
        """
        movement_type = validated_data["movement_type"]
        quantity = validated_data["quantity"]
        batch = validated_data.get("batch")

        if movement_type == StockMovementType.TRANSFER:
            if not validated_data.get("to_warehouse"):
                raise BusinessLogicException(
                    message=(
                        "TRANSFER requires to_warehouse."
                    )
                )
            if (
                batch
                and validated_data["to_warehouse"].pk
                == batch.warehouse_id
            ):
                raise BusinessLogicException(
                    message=(
                        "TRANSFER destination must differ from "
                        "the source batch warehouse."
                    )
                )

        # Validate stock availability for OUT / TRANSFER
        if movement_type in {
            StockMovementType.OUT,
            StockMovementType.TRANSFER,
        }:
            StockMovementService._validate_stock_out(
                validated_data=validated_data,
                quantity=quantity,
                batch=batch,
            )

        movement = StockMovement(
            movement_type=movement_type,
            status=MovementStatus.PENDING,
            product=validated_data["product"],
            quantity=quantity,
            unit_price=validated_data.get("unit_price", 0),
            batch=batch,
            from_warehouse=validated_data.get("from_warehouse"),
            to_warehouse=validated_data.get("to_warehouse"),
            reference_number=validated_data.get(
                "reference_number", ""
            ),
            notes=validated_data.get("notes", ""),
            performed_by=validated_data["performed_by"],
            movement_date=validated_data.get(
                "movement_date", timezone.now()
            ),
            created_by=validated_data["created_by"],
        )
        movement.save()
        return movement

    # --------------------------------------------------
    # RECORD PURCHASE RECEIPT (log-only COMPLETED movement)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def record_purchase_receipt(
        validated_data: dict,
        user=None,
    ) -> StockMovement:
        """
        Log a COMPLETED stock-IN movement after the caller has already
        applied the quantity change (typically via BatchService.create
        during purchase-invoice receiving).

        This method does **not** call `_apply_stock_change` and does **not**
        re-validate OUT/TRANSFER stock levels. Use it only when the
        inventory quantities have already been mutated by the caller.
        """
        if validated_data.get("movement_type") not in (
            None,
            StockMovementType.IN,
            StockMovementType.RETURN,
        ):
            # Default / force to IN for purchase receipts
            validated_data = {**validated_data, "movement_type": StockMovementType.IN}

        movement = StockMovement(
            movement_type=validated_data["movement_type"],
            status=MovementStatus.COMPLETED,
            product=validated_data["product"],
            quantity=validated_data["quantity"],
            unit_price=validated_data.get("unit_price", 0),
            batch=validated_data.get("batch"),
            from_warehouse=validated_data.get("from_warehouse"),
            to_warehouse=validated_data.get("to_warehouse"),
            reference_number=validated_data.get("reference_number", ""),
            notes=validated_data.get("notes", ""),
            performed_by=validated_data["performed_by"],
            movement_date=validated_data.get(
                "movement_date", timezone.now()
            ),
            created_by=validated_data["created_by"],
            completed_at=timezone.now(),
        )
        movement.save()
        return movement

    # --------------------------------------------------
    # UPDATE (status / metadata only)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        movement_id: int,
        validated_data: dict,
        user=None,
        partial: bool = False,
    ) -> StockMovement:
        movement = StockMovement.objects.select_for_update().get(
            pk=movement_id
        )

        if movement.status == MovementStatus.COMPLETED:
            raise BusinessLogicException(
                message=(
                    "Cannot update a completed stock movement."
                )
            )

        new_status = validated_data.get("status")

        fields = [
            "status",
            "approved_by",
            "reference_number",
            "notes",
        ]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(movement, field, validated_data[field])

        # If completing the movement, apply stock changes
        if new_status == MovementStatus.COMPLETED:
            StockMovementService._apply_stock_change(movement)
            movement.completed_at = timezone.now()

        movement.save()

        if new_status == MovementStatus.COMPLETED:
            from apps.accounting.services.event_service import (
                LedgerEventService,
            )

            # Ensure batch is available for cost lookup
            if movement.batch_id and movement.batch is None:
                movement.refresh_from_db()
            LedgerEventService.on_stock_movement_completed(
                movement, user=user
            )

        return movement

    # --------------------------------------------------
    # DELETE (only PENDING)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(movement_id: int) -> None:
        movement = StockMovement.objects.select_for_update().get(
            pk=movement_id
        )

        if movement.status != MovementStatus.PENDING:
            raise BusinessLogicException(
                message=(
                    "Only pending stock movements can be deleted."
                )
            )

        movement.delete()

    # --------------------------------------------------
    # INTERNAL HELPERS
    # --------------------------------------------------
    @staticmethod
    def _validate_stock_out(
        validated_data: dict,
        quantity,
        batch: Batch | None,
    ) -> None:
        """Ensure sufficient stock before creating OUT/TRANSFER."""
        if batch:
            locked_batch = Batch.objects.select_for_update().get(
                pk=batch.pk
            )
            if locked_batch.quantity < quantity:
                raise BusinessLogicException(
                    message=(
                        f"Insufficient batch stock. Available: "
                        f"{locked_batch.quantity}, "
                        f"requested: {quantity}."
                    )
                )
        else:
            product = validated_data["product"]
            # Sum available qty across all active batches
            # for this product in from_warehouse
            from_wh = validated_data.get("from_warehouse")
            available = (
                Batch.objects
                .filter(
                    variant__product=product,
                    warehouse=from_wh,
                    status="active",
                    is_active=True,
                )
                .aggregate(
                    total=models_sum("quantity")
                )["total"]
                or 0
            )
            if available < quantity:
                raise BusinessLogicException(
                    message=(
                        f"Insufficient warehouse stock. "
                        f"Available: {available}, "
                        f"requested: {quantity}."
                    )
                )

    @staticmethod
    def _apply_stock_change(movement: StockMovement) -> None:
        """
        Apply stock quantity changes when movement is completed.

        Source of truth: Batch.quantity (per warehouse).
        Variant.quantity is a denormalized total kept in sync here
        for IN / OUT / RETURN / ADJUSTMENT.

        TRANSFER moves quantity between warehouses without changing
        the variant total: source batch decreases, a target batch in
        ``to_warehouse`` is found or created and increased.
        """
        from apps.inventory.services.batch_service import BatchService

        movement_type = movement.movement_type
        qty = movement.quantity

        if not movement.batch:
            raise BusinessLogicException(
                message=(
                    "Cannot apply stock change: movement has no "
                    "batch. Assign a batch before completing."
                )
            )

        batch = Batch.objects.select_for_update().get(
            pk=movement.batch.pk
        )
        variant = Variant.objects.select_for_update().get(
            pk=batch.variant.pk
        )

        if movement_type in {
            StockMovementType.IN,
            StockMovementType.RETURN,
        }:
            batch.quantity += qty
            variant.quantity += qty

        elif movement_type == StockMovementType.OUT:
            if batch.quantity < qty:
                raise BusinessLogicException(
                    message=(
                        f"Insufficient batch stock to complete "
                        f"movement. Available: {batch.quantity}."
                    )
                )
            batch.quantity -= qty
            variant.quantity -= qty

        elif movement_type == StockMovementType.TRANSFER:
            if not movement.to_warehouse_id:
                raise BusinessLogicException(
                    message=(
                        "TRANSFER requires to_warehouse to be set."
                    )
                )
            if movement.to_warehouse_id == batch.warehouse_id:
                raise BusinessLogicException(
                    message=(
                        "TRANSFER destination warehouse must differ "
                        "from the source batch warehouse."
                    )
                )
            if batch.quantity < qty:
                raise BusinessLogicException(
                    message=(
                        f"Insufficient batch stock to complete "
                        f"transfer. Available: {batch.quantity}."
                    )
                )
            batch.quantity -= qty
            target = BatchService.get_or_create_target_batch(
                source_batch=batch,
                to_warehouse=movement.to_warehouse,
                user=movement.performed_by,
            )
            # Re-lock target in case get_or_create returned existing
            target = Batch.objects.select_for_update().get(pk=target.pk)
            target.quantity += qty
            target.save()
            # Variant total unchanged for warehouse-only transfer

        elif movement_type == StockMovementType.ADJUSTMENT:
            delta = qty - batch.quantity
            batch.quantity = qty
            variant.quantity += delta

        else:
            raise BusinessLogicException(
                message=f"Unsupported movement type: {movement_type}"
            )

        if batch.quantity < 0 or variant.quantity < 0:
            raise BusinessLogicException(
                message=(
                    "Stock change would result in negative quantity. "
                    f"Batch: {batch.quantity}, Variant: {variant.quantity}."
                )
            )

        batch.save()
        variant.save()
