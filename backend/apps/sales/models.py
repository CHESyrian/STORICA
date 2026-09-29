import uuid
from decimal import Decimal

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.core.validators import MinValueValidator
from django.contrib.auth import get_user_model

from apps.inventory.models import Variant

from common.models.base import (
    GeneralCodeModel, SimpleCodeModel
)
from common.models.choices import (
    OrderStatus, 
    InvoiceStatus, 
    PaymentStatus, 
)


# =========================================================
# USER
# =========================================================
User = get_user_model()

# =========================================================
# CUSTOMER
# =========================================================
class Customer(GeneralCodeModel):
    name = models.CharField(max_length=100)

    email = models.EmailField(blank=True, null=True, default="")
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)

    is_verified = models.BooleanField(default=False)

    notes = models.TextField(blank=True)


    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["email"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


# =========================================================
# SALES ORDER
# =========================================================
class SalesOrder(SimpleCodeModel):

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    order_date = models.DateTimeField(default=timezone.now)

    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.DRAFT.value,
    )

    notes = models.TextField(blank=True)


    class Meta:
        ordering = ["-order_date"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["status"]),
            models.Index(fields=["customer", "order_date"]),
        ]

    def __str__(self):
        return f"Order {self.code} - {self.customer.name}"

    def can_cancel(self):
        return self.status in {
            OrderStatus.DRAFT.value,
            OrderStatus.CONFIRMED.value,
            OrderStatus.PROCESSING.value,
        }


# =========================================================
# ORDER ITEM
# =========================================================
class SalesOrderItem(models.Model):
    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name="items",
    )

    variant = models.ForeignKey(
        Variant,
        on_delete=models.PROTECT,
        related_name="sales_items",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("1"))],
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["order", "variant"],
                name="unique_sales_order_variant",
            )
        ]
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["variant"]),
        ]

    def __str__(self):
        return f"{self.order.code} - {self.variant.name} x {self.quantity}"


# =========================================================
# INVOICE
# =========================================================
class SalesInvoice(SimpleCodeModel):

    order = models.OneToOneField(
        SalesOrder,
        on_delete=models.PROTECT,
        related_name="invoice",
        null=True,
        blank=True,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="invoices",
    )

    invoice_date = models.DateField(default=timezone.now)
    paid_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.DRAFT.value,
    )

    discount_rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10)

    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    notes = models.TextField(blank=True)


    class Meta:
        ordering = ["-invoice_date"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["status"]),
            models.Index(fields=["customer"]),
        ]

    def __str__(self):
        return f"Invoice {self.code} - {self.customer.name}"

    def save(self, *args, **kwargs):
        if self.amount_paid >= self.total_amount:
            self.status = InvoiceStatus.PAID.value
            self.paid_date = timezone.now().date()
            
        elif self.amount_paid > 0:
            self.status = InvoiceStatus.PARTIAL.value

        super().save(*args, **kwargs)


# =========================================================
# INVOICE ITEM
# =========================================================
class SalesInvoiceItem(models.Model):
    invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.CASCADE,
        related_name="items",
    )

    variant = models.ForeignKey(
        Variant,
        on_delete=models.PROTECT,
        related_name="sales",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    sale_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    discount_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

        indexes = [
            models.Index(fields=["invoice"]),
            models.Index(fields=["variant"]),
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["invoice", "variant"],
                name="unique_sales_invoice_variant",
            ),
        ]

    def __str__(self):
        return (
            f"{self.invoice.code} "
            f"- {self.variant}"
        )



# =========================================================
# PAYMENT
# =========================================================
class SalesPayment(models.Model):
    payment_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    transaction_id = models.CharField(max_length=100, unique=True, blank=True)

    invoice = models.ForeignKey(
        SalesInvoice,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    order = models.ForeignKey(
        SalesOrder,
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
    )

    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    payment_date = models.DateTimeField(default=timezone.now)

    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING.value,
    )

    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    processed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
    )

    class Meta:
        ordering = ["-payment_date"]
        indexes = [
            models.Index(fields=["payment_id"]),
            models.Index(fields=["transaction_id"]),
            models.Index(fields=["status", "payment_date"]),
            models.Index(fields=["invoice", "status"]),
        ]

    def __str__(self):
        return f"SalesPayment {self.payment_id} - {self.amount} ({self.status})"

