"""
Inventory tests — focus on stock movement correctness and concurrency safety.
"""
from decimal import Decimal
from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model

from common.exceptions.base import BusinessLogicException
from common.models.choices import (
    StockMovementType,
    MovementStatus,
    BatchStatus,
    WarehouseStatus,
    UnitChoices,
)

from apps.inventory.models import (
    Warehouse,
    Category,
    Product,
    Variant,
    Batch,
    StockMovement,
)
from apps.inventory.services.stock_movement_service import StockMovementService
from apps.inventory.services.batch_service import BatchService


User = get_user_model()


class StockMovementTestMixin:
    """Shared fixture helpers for stock movement tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="tester",
            password="pass12345",
            role="user",
        )
        self.warehouse = Warehouse.objects.create(
            name="Main WH",
            code="WH-MAIN",
            phone="000",
            status=WarehouseStatus.ACTIVE,
            created_by=self.user,
        )
        self.category = Category.objects.create(
            name="General",
            code="CAT-GEN",
            created_by=self.user,
        )
        self.product = Product.objects.create(
            name="Test Product",
            sku="SKU-001",
            category=self.category,
            unit=UnitChoices.PCS,
            created_by=self.user,
        )
        self.variant = Variant.objects.create(
            product=self.product,
            sku="VAR-001",
            name="Default",
            quantity=Decimal("0"),
            created_by=self.user,
        )

    def _make_batch(self, qty: Decimal = Decimal("100")) -> Batch:
        return BatchService.create(
            {
                "variant": self.variant,
                "warehouse": self.warehouse,
                "quantity": qty,
                "cost_price": Decimal("10.00"),
                "production_date": date.today(),
                "status": BatchStatus.ACTIVE,
            },
            user=self.user,
        )

    def _movement_data(self, batch: Batch, qty: Decimal, mtype: str, **extra):
        data = {
            "movement_type": mtype,
            "product": self.product,
            "quantity": qty,
            "unit_price": Decimal("10.00"),
            "batch": batch,
            "performed_by": self.user,
            "created_by": self.user,
            "notes": "test",
        }
        if mtype in (StockMovementType.OUT, StockMovementType.TRANSFER):
            data["from_warehouse"] = self.warehouse
        if mtype in (StockMovementType.IN, StockMovementType.RETURN, StockMovementType.TRANSFER):
            data.setdefault("to_warehouse", self.warehouse)
        data.update(extra)
        return data


class StockMovementCreateCompleteTests(StockMovementTestMixin, TestCase):
    """Happy-path and business-rule tests for create → complete."""

    def test_create_pending_does_not_change_stock(self):
        batch = self._make_batch(Decimal("50"))
        self.variant.refresh_from_db()
        initial_variant_qty = self.variant.quantity

        movement = StockMovementService.create(
            self._movement_data(batch, Decimal("10"), StockMovementType.OUT)
        )

        self.assertEqual(movement.status, MovementStatus.PENDING)
        batch.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal("50"))
        self.assertEqual(self.variant.quantity, initial_variant_qty)

    def test_complete_out_decreases_stock(self):
        batch = self._make_batch(Decimal("50"))
        movement = StockMovementService.create(
            self._movement_data(batch, Decimal("15"), StockMovementType.OUT)
        )

        StockMovementService.update(
            movement.pk,
            {"status": MovementStatus.COMPLETED},
            user=self.user,
        )

        batch.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal("35"))
        self.assertEqual(self.variant.quantity, Decimal("35"))
        movement.refresh_from_db()
        self.assertEqual(movement.status, MovementStatus.COMPLETED)
        self.assertIsNotNone(movement.completed_at)

    def test_complete_in_increases_stock(self):
        batch = self._make_batch(Decimal("20"))
        movement = StockMovementService.create(
            self._movement_data(batch, Decimal("30"), StockMovementType.IN)
        )

        StockMovementService.update(
            movement.pk,
            {"status": MovementStatus.COMPLETED},
            user=self.user,
        )

        batch.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal("50"))
        self.assertEqual(self.variant.quantity, Decimal("50"))

    def test_cannot_go_negative_on_complete(self):
        batch = self._make_batch(Decimal("10"))
        movement = StockMovementService.create(
            self._movement_data(batch, Decimal("10"), StockMovementType.OUT)
        )

        # Manually drain the batch so complete would go negative
        batch.quantity = Decimal("5")
        batch.save()

        with self.assertRaises(BusinessLogicException) as ctx:
            StockMovementService.update(
                movement.pk,
                {"status": MovementStatus.COMPLETED},
                user=self.user,
            )
        self.assertIn("Insufficient", str(ctx.exception.message))

    def test_create_out_rejects_insufficient_stock(self):
        batch = self._make_batch(Decimal("5"))
        with self.assertRaises(BusinessLogicException):
            StockMovementService.create(
                self._movement_data(batch, Decimal("10"), StockMovementType.OUT)
            )

    def test_cannot_update_completed_movement(self):
        batch = self._make_batch(Decimal("50"))
        movement = StockMovementService.create(
            self._movement_data(batch, Decimal("5"), StockMovementType.OUT)
        )
        StockMovementService.update(
            movement.pk,
            {"status": MovementStatus.COMPLETED},
            user=self.user,
        )
        with self.assertRaises(BusinessLogicException):
            StockMovementService.update(
                movement.pk,
                {"notes": "should fail"},
                user=self.user,
            )

    def test_delete_only_pending(self):
        batch = self._make_batch(Decimal("50"))
        movement = StockMovementService.create(
            self._movement_data(batch, Decimal("5"), StockMovementType.OUT)
        )
        StockMovementService.delete(movement.pk)
        self.assertFalse(StockMovement.objects.filter(pk=movement.pk).exists())

        movement2 = StockMovementService.create(
            self._movement_data(batch, Decimal("5"), StockMovementType.OUT)
        )
        StockMovementService.update(
            movement2.pk,
            {"status": MovementStatus.COMPLETED},
            user=self.user,
        )
        with self.assertRaises(BusinessLogicException):
            StockMovementService.delete(movement2.pk)

    def test_record_purchase_receipt_logs_without_double_apply(self):
        """BatchService already bumped quantities; receipt must only log."""
        batch = self._make_batch(Decimal("40"))  # already applied +40
        self.variant.refresh_from_db()
        qty_before = self.variant.quantity

        movement = StockMovementService.record_purchase_receipt(
            {
                "movement_type": StockMovementType.IN,
                "product": self.product,
                "quantity": Decimal("40"),
                "unit_price": Decimal("10.00"),
                "batch": batch,
                "to_warehouse": self.warehouse,
                "reference_number": "PO-001",
                "performed_by": self.user,
                "created_by": self.user,
                "notes": "from PO",
            },
            user=self.user,
        )

        self.assertEqual(movement.status, MovementStatus.COMPLETED)
        self.assertIsNotNone(movement.completed_at)
        batch.refresh_from_db()
        self.variant.refresh_from_db()
        # Quantities must stay exactly as BatchService left them
        self.assertEqual(batch.quantity, Decimal("40"))
        self.assertEqual(self.variant.quantity, qty_before)

    def test_complete_requires_batch(self):
        movement = StockMovement(
            movement_type=StockMovementType.IN,
            status=MovementStatus.PENDING,
            product=self.product,
            quantity=Decimal("5"),
            performed_by=self.user,
            created_by=self.user,
        )
        movement.save()
        with self.assertRaises(BusinessLogicException) as ctx:
            StockMovementService.update(
                movement.pk,
                {"status": MovementStatus.COMPLETED},
                user=self.user,
            )
        self.assertIn("no batch", str(ctx.exception.message).lower())


class StockMovementConcurrencyTests(StockMovementTestMixin, TestCase):
    """
    Verify select_for_update path prevents oversell when two OUT movements
    compete for the same batch (sequential completes; locking still applied).

    Note: formerly TransactionTestCase — switched to TestCase because the
    scenario is sequential and does not require real concurrent commits.
    Reintroduce TransactionTestCase + threads only if true parallelism is tested.
    """

    def test_concurrent_complete_does_not_oversell(self):
        batch = self._make_batch(Decimal("10"))

        m1 = StockMovementService.create(
            self._movement_data(batch, Decimal("8"), StockMovementType.OUT)
        )
        m2 = StockMovementService.create(
            self._movement_data(batch, Decimal("8"), StockMovementType.OUT)
        )

        # First complete succeeds
        StockMovementService.update(
            m1.pk, {"status": MovementStatus.COMPLETED}, user=self.user
        )
        batch.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal("2"))

        # Second complete must fail (only 2 left)
        with self.assertRaises(BusinessLogicException):
            StockMovementService.update(
                m2.pk, {"status": MovementStatus.COMPLETED}, user=self.user
            )

        batch.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal("2"))
        self.assertEqual(self.variant.quantity, Decimal("2"))


class StockTransferTests(StockMovementTestMixin, TestCase):
    """Full inter-warehouse TRANSFER keeps variant total stable."""

    def test_transfer_moves_qty_between_warehouses(self):
        from apps.inventory.models import Warehouse, Batch
        from common.models.choices import WarehouseStatus

        dest = Warehouse.objects.create(
            name="Secondary",
            code="WH-SEC",
            phone="111",
            status=WarehouseStatus.ACTIVE,
            created_by=self.user,
        )
        batch = self._make_batch(Decimal("40"))
        self.variant.refresh_from_db()
        start_variant = self.variant.quantity

        movement = StockMovementService.create(
            {
                **self._movement_data(
                    batch, Decimal("15"), StockMovementType.TRANSFER
                ),
                "to_warehouse": dest,
            },
            user=self.user,
        )
        StockMovementService.update(
            movement.pk,
            {"status": MovementStatus.COMPLETED},
            user=self.user,
        )

        batch.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal("25"))
        self.assertEqual(self.variant.quantity, start_variant)

        target = Batch.objects.get(
            variant=self.variant, warehouse=dest, is_active=True
        )
        self.assertEqual(target.quantity, Decimal("15"))

    def test_transfer_requires_to_warehouse(self):
        batch = self._make_batch(Decimal("10"))
        with self.assertRaises(BusinessLogicException):
            StockMovementService.create(
                self._movement_data(
                    batch, Decimal("5"), StockMovementType.TRANSFER
                ),
                user=self.user,
            )


class StockAdjustmentReturnTests(StockMovementTestMixin, TestCase):
    """ADJUSTMENT sets absolute qty; RETURN increases like IN."""

    def test_complete_return_increases_stock(self):
        batch = self._make_batch(Decimal("20"))
        self.variant.refresh_from_db()
        start_batch = batch.quantity
        start_variant = self.variant.quantity

        movement = StockMovementService.create(
            self._movement_data(
                batch, Decimal("7"), StockMovementType.RETURN
            ),
            user=self.user,
        )
        StockMovementService.update(
            movement.pk,
            {"status": MovementStatus.COMPLETED},
            user=self.user,
        )

        batch.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(batch.quantity, start_batch + Decimal("7"))
        self.assertEqual(self.variant.quantity, start_variant + Decimal("7"))

    def test_complete_adjustment_sets_absolute_quantity(self):
        batch = self._make_batch(Decimal("50"))
        self.variant.refresh_from_db()
        # Adjustment quantity is the new absolute batch qty (not a delta).
        movement = StockMovementService.create(
            self._movement_data(
                batch, Decimal("30"), StockMovementType.ADJUSTMENT
            ),
            user=self.user,
        )
        StockMovementService.update(
            movement.pk,
            {"status": MovementStatus.COMPLETED},
            user=self.user,
        )

        batch.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal("30"))
        # Variant decreased by 20 (50 -> 30)
        self.assertEqual(self.variant.quantity, Decimal("30"))

    def test_complete_adjustment_increase(self):
        batch = self._make_batch(Decimal("10"))
        self.variant.refresh_from_db()
        movement = StockMovementService.create(
            self._movement_data(
                batch, Decimal("40"), StockMovementType.ADJUSTMENT
            ),
            user=self.user,
        )
        StockMovementService.update(
            movement.pk,
            {"status": MovementStatus.COMPLETED},
            user=self.user,
        )
        batch.refresh_from_db()
        self.variant.refresh_from_db()
        self.assertEqual(batch.quantity, Decimal("40"))
        self.assertEqual(self.variant.quantity, Decimal("40"))


class StockStatusAndMinStockTests(StockMovementTestMixin, TestCase):
    """min_stock threshold and stock status aggregation."""

    def test_min_stock_default_and_update(self):
        from apps.inventory.services.variant_service import VariantService

        self.assertEqual(self.variant.min_stock, Decimal("0"))
        updated = VariantService.update(
            self.variant.pk,
            {"min_stock": Decimal("15")},
            user=self.user,
            partial=True,
        )
        self.assertEqual(updated.min_stock, Decimal("15"))

    def test_stock_status_flags_low_stock(self):
        from apps.inventory.services.stock_status_service import (
            StockStatusService,
        )
        from apps.inventory.services.variant_service import VariantService

        self._make_batch(Decimal("10"))
        VariantService.update(
            self.variant.pk,
            {"min_stock": Decimal("15")},
            user=self.user,
            partial=True,
        )

        rows = StockStatusService.list_status()
        self.assertTrue(rows)
        match = next(
            r for r in rows if r["variant"] == self.variant.pk
        )
        self.assertEqual(match["quantity"], Decimal("10"))
        self.assertEqual(match["min_stock"], Decimal("15"))
        self.assertTrue(match["is_low_stock"])

        low_only = StockStatusService.list_status(low_stock=True)
        self.assertTrue(any(r["variant"] == self.variant.pk for r in low_only))

    def test_stock_status_not_low_when_above_threshold(self):
        from apps.inventory.services.stock_status_service import (
            StockStatusService,
        )
        from apps.inventory.services.variant_service import VariantService

        self._make_batch(Decimal("100"))
        VariantService.update(
            self.variant.pk,
            {"min_stock": Decimal("15")},
            user=self.user,
            partial=True,
        )
        rows = StockStatusService.list_status()
        match = next(r for r in rows if r["variant"] == self.variant.pk)
        self.assertFalse(match["is_low_stock"])

