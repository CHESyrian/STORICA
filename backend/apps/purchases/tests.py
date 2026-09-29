"""
Purchases tests — Order → Invoice (receive stock) → Payment and cancel rules.
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
    UnitChoices,
    WarehouseStatus,
)

from apps.inventory.models import (
    Warehouse,
    Category,
    Product,
    Variant,
    Batch,
    StockMovement,
)
from apps.purchases.services.supplier_service import SupplierService
from apps.purchases.services.purchases_order_service import (
    PurchasesOrderService,
)
from apps.purchases.services.purchases_invoice_service import (
    PurchasesInvoiceService,
)
from apps.purchases.services.purchases_payment_service import (
    PurchasesPaymentService,
)


User = get_user_model()


class PurchasesFlowTestMixin:
    def setUp(self):
        self.user = User.objects.create_user(
            username="purch_tester",
            password="pass12345",
            role="user",
        )
        self.supplier = SupplierService.create(
            {
                "name": "Acme Supply",
                "email": "supply@acme.test",
                "phone": "555-0200",
                "address": "2 Warehouse Rd",
            },
            user=self.user,
        )
        self.warehouse = Warehouse.objects.create(
            name="Recv WH",
            code="WH-RECV",
            phone="000",
            status=WarehouseStatus.ACTIVE,
            created_by=self.user,
        )
        self.category = Category.objects.create(
            name="Goods",
            code="CAT-PUR",
            created_by=self.user,
        )
        self.product = Product.objects.create(
            name="Bolt",
            sku="SKU-B1",
            category=self.category,
            unit=UnitChoices.PCS,
            created_by=self.user,
        )
        self.variant = Variant.objects.create(
            product=self.product,
            sku="VAR-B1",
            name="M8",
            quantity=Decimal("0"),
            created_by=self.user,
        )

    def _order_data(self, qty: Decimal = Decimal("20")):
        return {
            "supplier": self.supplier,
            "notes": "test PO",
            "items": [
                {"variant": self.variant, "quantity": qty},
            ],
        }

    def _invoice_data(
        self,
        order=None,
        total: Decimal = Decimal("200.00"),
        amount_paid: Decimal = Decimal("0"),
        qty: Decimal = Decimal("20"),
    ):
        return {
            "supplier": self.supplier,
            "order": order,
            "warehouse": self.warehouse,
            "discount_rate": Decimal("0"),
            "tax_rate": Decimal("0"),
            "total_amount": total,
            "amount_paid": amount_paid,
            "notes": "test PI",
            "items": [
                {
                    "variant": self.variant,
                    "quantity": qty,
                    "cost_price": Decimal("10.00"),
                    "production_date": date.today(),
                    "expiry_date": None,
                    "discount_rate": Decimal("0"),
                    "tax_rate": Decimal("0"),
                },
            ],
        }


class PurchasesOrderInvoicePaymentTests(PurchasesFlowTestMixin, TestCase):

    def test_create_order_draft(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        self.assertEqual(order.status, OrderStatus.DRAFT.value)
        self.assertEqual(order.items.count(), 1)
        self.assertTrue(order.code)

    def test_cancel_order(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        cancelled = PurchasesOrderService.cancel(order.pk, user=self.user)
        self.assertEqual(cancelled.status, OrderStatus.CANCELLED.value)

    def test_invoice_create_receives_stock(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(order=order, qty=Decimal("20")),
            user=self.user,
        )
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.quantity, Decimal("20"))
        self.assertEqual(
            Batch.objects.filter(variant=self.variant).count(), 1
        )
        batch = Batch.objects.get(variant=self.variant)
        self.assertEqual(batch.quantity, Decimal("20"))
        self.assertEqual(batch.warehouse_id, self.warehouse.pk)
        self.assertTrue(
            StockMovement.objects.filter(
                reference_number=invoice.code,
                movement_type="in",
                status="completed",
            ).exists()
        )
        self.assertEqual(invoice.status, InvoiceStatus.SENT.value)

    def test_invoice_with_payment_sets_paid(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(
                order=order,
                total=Decimal("100.00"),
                amount_paid=Decimal("100.00"),
                qty=Decimal("10"),
            ),
            user=self.user,
        )
        self.assertEqual(invoice.status, InvoiceStatus.PAID.value)
        self.assertEqual(invoice.amount_paid, Decimal("100.00"))
        order.refresh_from_db()
        self.assertEqual(order.status, OrderStatus.COMPLETED.value)

    def test_second_invoice_same_order_rejected(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        PurchasesInvoiceService.create(
            self._invoice_data(order=order), user=self.user
        )
        with self.assertRaises(ConflictException):
            PurchasesInvoiceService.create(
                self._invoice_data(order=order), user=self.user
            )

    def test_post_invoice_idempotent(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(order=order), user=self.user
        )
        again = PurchasesInvoiceService.post_invoice(
            invoice.pk, user=self.user
        )
        self.assertEqual(again.pk, invoice.pk)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.quantity, Decimal("20"))

    def test_cannot_post_cancelled(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(order=order), user=self.user
        )
        invoice.status = InvoiceStatus.CANCELLED.value
        invoice.save()
        with self.assertRaises(BusinessLogicException):
            PurchasesInvoiceService.post_invoice(
                invoice.pk, user=self.user
            )

    def test_standalone_payment_updates_balance(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(
                order=order,
                total=Decimal("50.00"),
                amount_paid=Decimal("0"),
                qty=Decimal("5"),
            ),
            user=self.user,
        )
        PurchasesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "supplier": self.supplier,
                "amount": Decimal("20.00"),
                "processed_by": self.user,
            },
            user=self.user,
            adjust_invoice_balance=True,
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("20.00"))


    def test_cancel_sent_invoice_reverses_stock(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(order=order, qty=Decimal("20")),
            user=self.user,
        )
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.quantity, Decimal("20"))

        cancelled = PurchasesInvoiceService.cancel(
            invoice.pk, user=self.user
        )
        self.assertEqual(cancelled.status, InvoiceStatus.CANCELLED.value)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.quantity, Decimal("0"))

    def test_cannot_cancel_paid_invoice(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(
                order=order,
                total=Decimal("100.00"),
                amount_paid=Decimal("100.00"),
                qty=Decimal("10"),
            ),
            user=self.user,
        )
        with self.assertRaises(BusinessLogicException):
            PurchasesInvoiceService.cancel(invoice.pk, user=self.user)

    def test_payment_without_order_uses_invoice_order(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(
                order=order,
                total=Decimal("50.00"),
                amount_paid=Decimal("0"),
                qty=Decimal("5"),
            ),
            user=self.user,
        )
        payment = PurchasesPaymentService.create(
            {
                "invoice": invoice,
                # order omitted — should fall back to invoice.order
                "supplier": self.supplier,
                "amount": Decimal("10.00"),
                "processed_by": self.user,
            },
            user=self.user,
            adjust_invoice_balance=True,
        )
        self.assertEqual(payment.order_id, order.pk)
        self.assertEqual(payment.status, "partial")
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("10.00"))

    def test_refund_payment_restores_balance(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(
                order=order,
                total=Decimal("50.00"),
                amount_paid=Decimal("0"),
                qty=Decimal("5"),
            ),
            user=self.user,
        )
        payment = PurchasesPaymentService.create(
            {
                "invoice": invoice,
                "order": order,
                "supplier": self.supplier,
                "amount": Decimal("50.00"),
                "processed_by": self.user,
            },
            user=self.user,
            adjust_invoice_balance=True,
        )
        invoice.refresh_from_db()
        self.assertEqual(invoice.status, InvoiceStatus.PAID.value)

        refunded = PurchasesPaymentService.refund(
            payment.pk, user=self.user
        )
        self.assertEqual(refunded.status, "refunded")
        invoice.refresh_from_db()
        self.assertEqual(invoice.amount_paid, Decimal("0"))
        self.assertEqual(invoice.status, InvoiceStatus.SENT.value)

    def test_confirm_order(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        confirmed = PurchasesOrderService.confirm(
            order.pk, user=self.user
        )
        self.assertEqual(confirmed.status, OrderStatus.CONFIRMED.value)

    def test_invoice_total_computed_from_lines(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        # Client total wrong; lines are 20 * 10 = 200
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(
                order=order,
                total=Decimal("999.00"),
                qty=Decimal("20"),
            ),
            user=self.user,
        )
        self.assertEqual(invoice.total_amount, Decimal("200.00"))

    def test_cannot_update_amounts_after_receive(self):
        order = PurchasesOrderService.create(
            self._order_data(), user=self.user
        )
        invoice = PurchasesInvoiceService.create(
            self._invoice_data(order=order),
            user=self.user,
        )
        with self.assertRaises(BusinessLogicException):
            PurchasesInvoiceService.update(
                invoice.pk,
                {"total_amount": Decimal("1.00")},
                user=self.user,
            )
