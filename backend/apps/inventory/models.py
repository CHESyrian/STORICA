import uuid
from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.contrib.auth import get_user_model

from common.models.base import (
    GeneralCodeModel, 
    GeneralSKUModel,  
)
from common.models.choices import (
    WarehouseStatus, 
    BatchStatus, 
    StockMovementType, 
    MovementStatus, 
    UnitChoices, 
)


# =========================================================
# USER
# =========================================================
User = get_user_model()

# =================================================
# WAREHOUSE
# =================================================
class Warehouse(GeneralCodeModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    location = models.TextField(blank=True)
    phone = models.CharField(max_length=20)

    status = models.CharField(
        max_length=20,
        choices=WarehouseStatus.choices,
        default=WarehouseStatus.ACTIVE,
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


# =================================================
# CATEGORY
# =================================================
class Category(GeneralCodeModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


# =================================================
# PRODUCT
# =================================================
class Product(GeneralSKUModel):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    unit = models.CharField(
        max_length=10,
        choices=UnitChoices.choices,
        default=UnitChoices.PCS,
    )

    notes = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="products/",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["category"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.sku} - {self.name}"


# =================================================
# VARIANT
# =================================================
class Variant(GeneralSKUModel):
    """
    Product variant (size/color/etc.).

    quantity is a denormalized cache of the sum of related
    Batch.quantity values. Update it only inside inventory services
    (StockMovementService / BatchService) under select_for_update.
    Prefer Batch.quantity as the source of truth for warehouse stock.
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants",
    )

    name  = models.CharField(max_length=200, blank=True)

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        default=0,
        help_text=(
            "Denormalized total stock across all batches. "
            "Updated only by inventory services."
        ),
    )

    min_stock = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        default=0,
        help_text=(
            "Reorder threshold. Stock status flags rows as low "
            "when on-hand quantity is at or below this level."
        ),
    )

    color = models.CharField(max_length=200, blank=True, null=True)

    weight = models.DecimalField(
        max_digits=10,
        decimal_places=3,
        null=True,
        blank=True,
    )

    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["product", "sku"]
        indexes = [
            models.Index(fields=["sku"]),
            models.Index(fields=["product"]),
            models.Index(fields=["is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "sku"],
                name="unique_product_variant_sku",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=0),
                name="variant_quantity_non_negative",
            ),
            models.CheckConstraint(
                condition=models.Q(min_stock__gte=0),
                name="variant_min_stock_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.product.sku} - {self.sku}"


# =================================================
# BATCH
# =================================================
class Batch(GeneralCodeModel):
    SLUG_SOURCE_FIELD = "code"

    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE,
        related_name="batches",
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.CASCADE,
        related_name="batches",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Source-of-truth stock quantity for this batch in its warehouse.",
    )
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)

    production_date = models.DateField()
    expiry_date     = models.DateField(null=True, blank=True)
    received_date   = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=BatchStatus.choices,
        default=BatchStatus.ACTIVE,
    )

    class Meta:
        ordering = ["expiry_date"]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["expiry_date"]),
            models.Index(fields=["variant", "warehouse"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=0),
                name="batch_quantity_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.variant}"

    def is_expired(self):
        return (
            self.expiry_date
            and self.expiry_date < timezone.now().date()
        )


# =================================================
# STOCK MOVEMENT
# =================================================
class StockMovement(models.Model):
    movement_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    movement_type = models.CharField(
        max_length=20,
        choices=StockMovementType.choices,
    )

    status = models.CharField(
        max_length=20,
        choices=MovementStatus.choices,
        default=MovementStatus.PENDING,
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name="movements",
    )

    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
        help_text="Movement quantity (must be >= 0).",
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    from_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="out_movements",
        null=True,
        blank=True,
    )

    to_warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT,
        related_name="in_movements",
        null=True,
        blank=True,
    )

    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    performed_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="movements",
    )

    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    movement_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="movements_created",
        help_text="User who created this record"
    )

    class Meta:
        ordering = ["-movement_date"]
        indexes = [
            models.Index(fields=["movement_id"]),
            models.Index(fields=["movement_type"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(quantity__gte=0),
                name="stock_movement_quantity_non_negative",
            ),
        ]

    @property
    def total_cost(self):
        """Quantity × unit_price (safe for missing/None values)."""
        quantity = self.quantity or Decimal("0")
        unit_price = self.unit_price or Decimal("0")
        return quantity * unit_price

    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product}"