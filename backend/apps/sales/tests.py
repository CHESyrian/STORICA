"""
Sales tests — Order → Invoice → Payment happy path and cancellation rules.
"""
from decimal import Decimal
from datetime import date

from django.test import TestCase
from django.contrib.auth import get_user_model

from common.exceptions.base import (
    BusinessLogicException,
    ConflictException,
)
from common.models.choices import (
    OrderStatus,
    InvoiceStatus,
    PaymentStatus,
    UnitChoices,
    WarehouseStatus,
    BatchStatus,
)

from apps.inventory.models import (
    Warehouse,
    Category,
    Product,
    Variant,
)
from apps.inventory.services.batch_service import BatchService
from apps.sales.models import (
    Customer,
    SalesOrder,
    SalesInvoice,
    SalesPayment,
)
from apps.sales.services.customer_service import CustomerService
from apps.sales.services.sales_order_service import SalesOrderService
from apps.sales.services.sales_invoice_service import SalesInvoiceService
from apps.sales.services.sales_payment_service import SalesPaymentService


User = get_user_model()


class SalesFlowTestMixin:
    """Shared fixtures for sales order / invoice / payment tests."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="sales_tester",
            password="pass12345",
            role="user",
        )
        self.manager = User.objects.create_user(
            username="sales_manager",
            password="pass12345",
            role="manager",
        )

        self.customer = CustomerService.create(
            {
                "name": "Acme Retail",
                "email": "buyer@acme.test",
                "phone": "555-0100",
                "address": "1 Market St",
            },
            user=self.user,
        )

        self.warehouse = Warehouse.objects.create(
            name="Main WH",
            code="WH-SALES",
            phone="000",
            status=WarehouseStatus.ACTIVE,
            created_by=self.user,
        )
        self.category = Category.objects.create(
            name="Goods",
            code="CAT-SALES",
            created_by=self.user,
        )
        self.product = Product.objects.create(
            name="Widget",
            sku="SKU-W1",
            category=self.category,
            unit=UnitChoices.PCS,
            created_by=self.user,
        )
        self.variant = Variant.objects.create(
            product=self.product,
            sku="VAR-W1",
            name="Standard",
            quantity=Decimal("0"),
            created_by=self.user,
        )
        # Seed stock so downstream posting could work later
        BatchService.create(
            {
                "variant": self.variant,
                "warehouse": self.warehouse,
                "quantity": Decimal("100"),
                "cost_price": Decimal("5.00"),
                "production_date": date.today(),
                "status": BatchStatus.ACTIVE,
            },
            user=self.user,
        )

    def _order_data(self, qty: Decimal = Decimal("10")):
        return {
            "customer": self.customer,
            "notes": "test order",
            "items": [
                {"variant": self.variant, "quantity": qty},
            ],
        }

    def _invoice_data(
        self,
        order: SalesOrder,
        total: Decimal = Decimal("110.00"),
        *,
        quantity: Decimal = Decimal("10"),
        sale_price: Decimal = Decimal("10.00"),
        item_tax_rate: Decimal = Decimal("10"),
    ):
        # total is optional client hint; service recomputes from lines.
        return {
            "customer": self.customer,
            "order": order,
            "discount_rate": Decimal("0"),
            "tax_rate": Decimal("10"),
            "total_amount": total,
            "amount_paid": Decimal("0"),
            "notes": "test invoice",
            "items": [
                {
                    "variant": self.variant,
                    "quantity": quantity,
                    "sale_price": sale_price,
                    "discount_rate": Decimal("0"),
                    "tax_rate": item_tax_rate,
                },
            ],
        }


class SalesOrderInvoicePaymentHappyPathTests(SalesFlowTestMixin, TestCase):
    """Order → Invoice → Payment happy path."""

    def test_create_order_draft_with_items(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)

        self.assertEqual(order.status, OrderStatus.DRAFT.value)
        self.assertTrue(order.code)
        self.assertEqual(order.customer_id, self.customer.pk)
        self.assertEqual(order.items.count(), 1)
        item = order.items.first()
        self.assertEqual(item.variant_id, self.variant.pk)
        self.assertEqual(item.quantity, Decimal("10"))

    def test_confirm_order(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        updated = SalesOrderService.update(
            order.pk,
            {"status": OrderStatus.CONFIRMED.value},
            user=self.user,
        )
        self.assertEqual(updated.status, OrderStatus.CONFIRMED.value)

    def test_create_invoice_from_order(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        SalesOrderService.update(
            order.pk,
            {"status": OrderStatus.CONFIRMED.value},
            user=self.user,
        )

        invoice = SalesInvoiceService.create(
            self._invoice_data(order),
            user=self.user,
        )

        self.assertEqual(invoice.status, InvoiceStatus.DRAFT.value)
        self.assertEqual(invoice.order_id, order.pk)
        self.assertEqual(invoice.total_amount, Decimal("110.00"))
        self.assertEqual(invoice.amount_paid, Decimal("0"))
        self.assertEqual(invoice.items.count(), 1)
        self.assertTrue(invoice.code)

    def test_cannot_create_second_invoice_for_same_order(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        SalesInvoiceService.create(self._invoice_data(order), user=self.user)

        with self.assertRaises(ConflictException) as ctx:
            SalesInvoiceService.create(self._invoice_data(order), user=self.user)
        self.assertIn("already exists", str(ctx.exception.message).lower())

    def test_payment_updates_invoice_balance_and_status(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        # 10 * 10 * 1.0 = 100 (no item tax)
        invoice = SalesInvoiceService.create(
            self._invoice_data(
                order,
                total=Decimal("100.00"),
                item_tax_rate=Decimal("0"),
            ),
            user=self.user,
        )
        self.assertEqual(invoice.total_amount, Decimal("100.00"))

        # Partial payment — applied immediately as COMPLETED
        payment1 = SalesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "customer": self.customer,
                "amount": Decimal("40.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-PARTIAL-1",
            },
            user=self.user,
        )
        invoice.refresh_from_db()
        self.assertEqual(payment1.status, PaymentStatus.COMPLETED.value)
        self.assertEqual(invoice.amount_paid, Decimal("40.00"))
        self.assertEqual(invoice.status, InvoiceStatus.PARTIAL.value)

        # Remaining balance
        payment2 = SalesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "customer": self.customer,
                "amount": Decimal("60.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-FULL-2",
            },
            user=self.user,
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("100.00"))
        self.assertEqual(invoice.status, InvoiceStatus.PAID.value)
        self.assertIsNotNone(invoice.paid_date)
        self.assertEqual(payment2.amount, Decimal("60.00"))
        self.assertEqual(payment2.status, PaymentStatus.COMPLETED.value)

    def test_payment_rejects_overpay(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(
                order,
                total=Decimal("50.00"),
                quantity=Decimal("5"),
                sale_price=Decimal("10.00"),
                item_tax_rate=Decimal("0"),
            ),
            user=self.user,
        )
        self.assertEqual(invoice.total_amount, Decimal("50.00"))

        with self.assertRaises(BusinessLogicException) as ctx:
            SalesPaymentService.create(
                {
                    "invoice": invoice,
                    "order": order,
                    "customer": self.customer,
                    "amount": Decimal("50.01"),
                    "processed_by": self.user,
                },
                user=self.user,
            )
        self.assertIn("exceeds remaining", str(ctx.exception.message).lower())

    def test_full_happy_path_order_invoice_payment(self):
        """End-to-end: draft order → confirm → invoice → full payment → paid."""
        order = SalesOrderService.create(self._order_data(), user=self.user)
        self.assertEqual(order.status, OrderStatus.DRAFT.value)

        order = SalesOrderService.update(
            order.pk,
            {"status": OrderStatus.CONFIRMED.value},
            user=self.user,
        )
        self.assertEqual(order.status, OrderStatus.CONFIRMED.value)

        invoice = SalesInvoiceService.create(
            self._invoice_data(order, total=Decimal("110.00")),
            user=self.user,
        )
        self.assertEqual(invoice.status, InvoiceStatus.DRAFT.value)

        SalesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "customer": self.customer,
                "amount": Decimal("110.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-HAPPY",
            },
            user=self.user,
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("110.00"))
        self.assertEqual(invoice.status, InvoiceStatus.PAID.value)


class SalesCancellationRulesTests(SalesFlowTestMixin, TestCase):
    """Cancellation and delete rules for orders, invoices, payments."""

    def test_cancel_draft_order(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        cancelled = SalesOrderService.cancel(order.pk, user=self.user)
        self.assertEqual(cancelled.status, OrderStatus.CANCELLED.value)

    def test_cancel_confirmed_order(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        SalesOrderService.update(
            order.pk,
            {"status": OrderStatus.CONFIRMED.value},
            user=self.user,
        )
        cancelled = SalesOrderService.cancel(order.pk, user=self.user)
        self.assertEqual(cancelled.status, OrderStatus.CANCELLED.value)

    def test_cannot_cancel_completed_order(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        SalesOrderService.update(
            order.pk,
            {"status": OrderStatus.COMPLETED.value},
            user=self.user,
        )
        with self.assertRaises(BusinessLogicException) as ctx:
            SalesOrderService.cancel(order.pk, user=self.user)
        self.assertIn("cannot cancel", str(ctx.exception.message).lower())

    def test_cannot_update_cancelled_order(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        SalesOrderService.cancel(order.pk, user=self.user)
        with self.assertRaises(BusinessLogicException):
            SalesOrderService.update(
                order.pk,
                {"notes": "should fail"},
                user=self.user,
            )

    def test_delete_only_draft_or_cancelled_order(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        SalesOrderService.delete(order.pk, user=self.user)
        order.refresh_from_db()
        self.assertFalse(order.is_active)

        order2 = SalesOrderService.create(self._order_data(), user=self.user)
        SalesOrderService.update(
            order2.pk,
            {"status": OrderStatus.CONFIRMED.value},
            user=self.user,
        )
        with self.assertRaises(BusinessLogicException):
            SalesOrderService.delete(order2.pk, user=self.user)

    def test_cannot_update_cancelled_invoice(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(order),
            user=self.user,
        )
        invoice.status = InvoiceStatus.CANCELLED.value
        invoice.save()

        with self.assertRaises(BusinessLogicException):
            SalesInvoiceService.update(
                invoice.pk,
                {"notes": "nope"},
                user=self.user,
            )

    def test_delete_only_draft_or_cancelled_invoice(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(order),
            user=self.user,
        )
        SalesInvoiceService.delete(invoice.pk, user=self.user)
        invoice.refresh_from_db()
        self.assertFalse(invoice.is_active)

        order2 = SalesOrderService.create(self._order_data(), user=self.user)
        invoice2 = SalesInvoiceService.create(
            self._invoice_data(
                order2,
                total=Decimal("50.00"),
                quantity=Decimal("5"),
                sale_price=Decimal("10.00"),
                item_tax_rate=Decimal("0"),
            ),
            user=self.user,
        )
        # Force non-draft status via payment path
        SalesPaymentService.create(
            {
                "invoice": invoice2,
                "order": order2,
                "customer": self.customer,
                "amount": Decimal("50.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-PAID-DEL",
            },
            user=self.user,
        )
        invoice2.refresh_from_db()
        self.assertEqual(invoice2.status, InvoiceStatus.PAID.value)
        with self.assertRaises(BusinessLogicException):
            SalesInvoiceService.delete(invoice2.pk, user=self.user)

    def test_cannot_delete_completed_payment(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(
                order,
                total=Decimal("30.00"),
                quantity=Decimal("3"),
                sale_price=Decimal("10.00"),
                item_tax_rate=Decimal("0"),
            ),
            user=self.user,
        )
        # Payments are COMPLETED on create
        payment = SalesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "customer": self.customer,
                "amount": Decimal("30.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-COMPLETE",
            },
            user=self.user,
        )
        self.assertEqual(payment.status, PaymentStatus.COMPLETED.value)
        with self.assertRaises(BusinessLogicException):
            SalesPaymentService.delete(payment.pk)

    def test_cannot_delete_completed_payment_restores_nothing(self):
        """Completed payments cannot be deleted; balance stays."""
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(
                order,
                total=Decimal("80.00"),
                quantity=Decimal("8"),
                sale_price=Decimal("10.00"),
                item_tax_rate=Decimal("0"),
            ),
            user=self.user,
        )
        payment = SalesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "customer": self.customer,
                "amount": Decimal("25.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-REV",
            },
            user=self.user,
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("25.00"))
        self.assertEqual(payment.status, PaymentStatus.COMPLETED.value)

        with self.assertRaises(BusinessLogicException):
            SalesPaymentService.delete(payment.pk)
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("25.00"))
        self.assertTrue(SalesPayment.objects.filter(pk=payment.pk).exists())

    def test_duplicate_transaction_id_rejected(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(
                order,
                total=Decimal("100.00"),
                item_tax_rate=Decimal("0"),
            ),
            user=self.user,
        )
        SalesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "customer": self.customer,
                "amount": Decimal("10.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-DUP",
            },
            user=self.user,
        )
        with self.assertRaises(ConflictException):
            SalesPaymentService.create(
                {
                    "invoice": invoice,
                    "order": order,
                    "customer": self.customer,
                    "amount": Decimal("10.00"),
                    "processed_by": self.user,
                    "transaction_id": "TXN-DUP",
                },
                user=self.user,
            )



    def test_refund_payment_restores_balance(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(
                order,
                total=Decimal("50.00"),
                quantity=Decimal("5"),
                sale_price=Decimal("10.00"),
                item_tax_rate=Decimal("0"),
            ),
            user=self.user,
        )
        payment = SalesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "customer": self.customer,
                "amount": Decimal("50.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-REFUND-1",
            },
            user=self.user,
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, InvoiceStatus.PAID.value)

        refunded = SalesPaymentService.refund(payment.pk, user=self.user)
        self.assertEqual(refunded.status, PaymentStatus.REFUNDED.value)
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("0"))
        self.assertEqual(invoice.status, InvoiceStatus.SENT.value)

    def test_cannot_refund_twice(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(
                order,
                total=Decimal("50.00"),
                quantity=Decimal("5"),
                sale_price=Decimal("10.00"),
                item_tax_rate=Decimal("0"),
            ),
            user=self.user,
        )
        payment = SalesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "customer": self.customer,
                "amount": Decimal("50.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-REFUND-2",
            },
            user=self.user,
        )
        SalesPaymentService.refund(payment.pk, user=self.user)
        with self.assertRaises(BusinessLogicException):
            SalesPaymentService.refund(payment.pk, user=self.user)



class SalesPostInvoiceTests(SalesFlowTestMixin, TestCase):
    """FIFO stock-out when posting a sales invoice."""

    def test_post_invoice_deducts_fifo_stock(self):
        # Seed stock via purchase-style batch
        from apps.inventory.services.batch_service import BatchService
        from common.models.choices import BatchStatus, MovementStatus

        BatchService.create(
            {
                "variant": self.variant,
                "warehouse": self.warehouse,
                "quantity": Decimal("50"),
                "cost_price": Decimal("5.00"),
                "production_date": date.today(),
                "status": BatchStatus.ACTIVE,
            },
            user=self.user,
        )
        self.variant.refresh_from_db()
        start_qty = self.variant.quantity

        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(order, total=Decimal("110.00")),
            user=self.user,
        )
        self.assertEqual(invoice.status, InvoiceStatus.DRAFT.value)

        posted = SalesInvoiceService.post_invoice(
            invoice.pk, user=self.user
        )
        self.assertEqual(posted.status, InvoiceStatus.SENT.value)

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.quantity, start_qty - Decimal("10"))

        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.PROCESSING.value)

        from apps.inventory.models import StockMovement
        self.assertTrue(
            StockMovement.objects.filter(
                reference_number=invoice.code,
                movement_type="out",
                status=MovementStatus.COMPLETED,
            ).exists()
        )

    def test_post_invoice_insufficient_stock(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(order),
            user=self.user,
        )
        # No stock seeded beyond setUp batch of 100 — reduce to 0
        from apps.inventory.models import Batch
        Batch.objects.filter(variant=self.variant).update(quantity=0)
        self.variant.quantity = 0
        self.variant.save()

        with self.assertRaises(BusinessLogicException) as ctx:
            SalesInvoiceService.post_invoice(invoice.pk, user=self.user)
        self.assertIn("insufficient", str(ctx.exception.message).lower())

    def test_cannot_post_paid_invoice(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(
                order,
                total=Decimal("50.00"),
                quantity=Decimal("5"),
                sale_price=Decimal("10.00"),
                item_tax_rate=Decimal("0"),
            ),
            user=self.user,
        )
        SalesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "customer": self.customer,
                "amount": Decimal("50.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-POST-PAID",
            },
            user=self.user,
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, InvoiceStatus.PAID.value)
        with self.assertRaises(BusinessLogicException):
            SalesInvoiceService.post_invoice(invoice.pk, user=self.user)

    def test_cannot_post_already_sent_invoice(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(order),
            user=self.user,
        )
        SalesInvoiceService.post_invoice(invoice.pk, user=self.user)
        with self.assertRaises(BusinessLogicException) as ctx:
            SalesInvoiceService.post_invoice(invoice.pk, user=self.user)
        self.assertIn("draft", str(ctx.exception.message).lower())

    def test_cancel_draft_invoice(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(order),
            user=self.user,
        )
        cancelled = SalesInvoiceService.cancel(invoice.pk, user=self.user)
        self.assertEqual(cancelled.status, InvoiceStatus.CANCELLED.value)

    def test_cancel_sent_invoice_reverses_stock(self):
        from apps.inventory.models import Batch

        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(order),
            user=self.user,
        )
        SalesInvoiceService.post_invoice(invoice.pk, user=self.user)
        self.variant.refresh_from_db()
        qty_after_post = self.variant.quantity

        cancelled = SalesInvoiceService.cancel(invoice.pk, user=self.user)
        self.assertEqual(cancelled.status, InvoiceStatus.CANCELLED.value)
        self.variant.refresh_from_db()
        # Stock restored by RETURN movement
        self.assertEqual(
            self.variant.quantity,
            qty_after_post + Decimal("10"),
        )
        self.assertTrue(Batch.objects.filter(variant=self.variant).exists())

    def test_cannot_cancel_paid_invoice(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        invoice = SalesInvoiceService.create(
            self._invoice_data(
                order,
                total=Decimal("50.00"),
                quantity=Decimal("5"),
                sale_price=Decimal("10.00"),
                item_tax_rate=Decimal("0"),
            ),
            user=self.user,
        )
        SalesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "customer": self.customer,
                "amount": Decimal("50.00"),
                "processed_by": self.user,
                "transaction_id": "TXN-NO-CANCEL",
            },
            user=self.user,
        )
        with self.assertRaises(BusinessLogicException):
            SalesInvoiceService.cancel(invoice.pk, user=self.user)

    def test_confirm_and_complete_order(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        confirmed = SalesOrderService.confirm(order.pk, user=self.user)
        self.assertEqual(confirmed.status, OrderStatus.CONFIRMED.value)

        # Move to processing via invoice post, then complete
        invoice = SalesInvoiceService.create(
            self._invoice_data(order),
            user=self.user,
        )
        SalesInvoiceService.post_invoice(invoice.pk, user=self.user)
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.PROCESSING.value)

        completed = SalesOrderService.complete(order.pk, user=self.user)
        self.assertEqual(completed.status, OrderStatus.COMPLETED.value)

    def test_cannot_confirm_non_draft_order(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        SalesOrderService.confirm(order.pk, user=self.user)
        with self.assertRaises(BusinessLogicException):
            SalesOrderService.confirm(order.pk, user=self.user)

    def test_invoice_total_computed_from_lines(self):
        order = SalesOrderService.create(self._order_data(), user=self.user)
        # Client sends wrong total; service recomputes 10*10*1.1 = 110
        invoice = SalesInvoiceService.create(
            self._invoice_data(order, total=Decimal("999.00")),
            user=self.user,
        )
        self.assertEqual(invoice.total_amount, Decimal("110.00"))
