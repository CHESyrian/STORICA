"""
Stock status aggregation — on-hand quantities by variant × warehouse.

Batch.quantity is the source of truth. This service groups active batches
and returns a flat list suitable for the Stock Status UI tab.
"""
from decimal import Decimal

from django.db.models import (
    Sum,
    Count,
    Min,
    Max,
    Q,
    F,
    DecimalField,
    ExpressionWrapper,
)

from common.models.choices import BatchStatus

from apps.inventory.models import Batch


class StockStatusService:
    """Read-only aggregation over Batch rows."""

    @staticmethod
    def list_status(
        *,
        search: str | None = None,
        warehouse_id: int | None = None,
        category_id: int | None = None,
        product_id: int | None = None,
        variant_id: int | None = None,
        is_active: bool | None = True,
        zero_stock: bool = False,
        low_stock: bool = False,
        ordering: str | None = None,
    ) -> list[dict]:
        """
        Aggregate active batches grouped by (variant, warehouse).

        Returns a list of dicts with keys:
          variant, variant_sku, variant_name, product, product_name,
          product_sku, category, category_name, warehouse, warehouse_name,
          warehouse_code, quantity, min_stock, is_low_stock, batch_count,
          earliest_expiry, latest_production, cost_value
        """
        qs = (
            Batch.objects
            .select_related(
                "variant__product__category",
                "warehouse",
            )
            .filter(status=BatchStatus.ACTIVE)
        )

        # Default (True) and explicit False both filter; only None means "no filter".
        if is_active is not None:
            qs = qs.filter(is_active=is_active)

        if warehouse_id is not None:
            qs = qs.filter(warehouse_id=warehouse_id)

        if variant_id is not None:
            qs = qs.filter(variant_id=variant_id)

        if product_id is not None:
            qs = qs.filter(variant__product_id=product_id)

        if category_id is not None:
            qs = qs.filter(variant__product__category_id=category_id)

        if search:
            qs = qs.filter(
                Q(variant__sku__icontains=search)
                | Q(variant__name__icontains=search)
                | Q(variant__product__name__icontains=search)
                | Q(variant__product__sku__icontains=search)
                | Q(warehouse__name__icontains=search)
                | Q(warehouse__code__icontains=search)
                | Q(code__icontains=search)
            )

        if not zero_stock:
            qs = qs.filter(quantity__gt=0)

        grouped = (
            qs.values(
                "variant_id",
                "variant__sku",
                "variant__name",
                "variant__min_stock",
                "variant__product_id",
                "variant__product__name",
                "variant__product__sku",
                "variant__product__category_id",
                "variant__product__category__name",
                "warehouse_id",
                "warehouse__name",
                "warehouse__code",
            )
            .annotate(
                # Annotate cost_value first so F("quantity") still refers to
                # the model field (not the quantity=Sum annotation below).
                cost_value=Sum(
                    ExpressionWrapper(
                        F("quantity") * F("cost_price"),
                        output_field=DecimalField(
                            max_digits=18, decimal_places=2
                        ),
                    )
                ),
                quantity=Sum("quantity"),
                batch_count=Count("id"),
                earliest_expiry=Min("expiry_date"),
                latest_production=Max("production_date"),
            )
        )

        # Push low-stock filter into SQL (HAVING on the Sum annotation)
        # so large catalogs do not pull every group into Python.
        if low_stock:
            grouped = grouped.filter(
                quantity__lte=F("variant__min_stock"),
                variant__min_stock__gt=0,
            )

        rows: list[dict] = []
        for row in grouped:
            qty = row["quantity"] or Decimal("0")
            min_stock = row["variant__min_stock"] or Decimal("0")
            rows.append(
                {
                    "variant": row["variant_id"],
                    "variant_sku": row["variant__sku"] or "",
                    "variant_name": row["variant__name"] or "",
                    "product": row["variant__product_id"],
                    "product_name": row["variant__product__name"] or "",
                    "product_sku": row["variant__product__sku"] or "",
                    "category": row["variant__product__category_id"],
                    "category_name": (
                        row["variant__product__category__name"] or ""
                    ),
                    "warehouse": row["warehouse_id"],
                    "warehouse_name": row["warehouse__name"] or "",
                    "warehouse_code": row["warehouse__code"] or "",
                    "quantity": qty,
                    "min_stock": min_stock,
                    "is_low_stock": bool(min_stock > 0 and qty <= min_stock),
                    "batch_count": row["batch_count"] or 0,
                    "earliest_expiry": row["earliest_expiry"],
                    "latest_production": row["latest_production"],
                    "cost_value": row["cost_value"] or Decimal("0"),
                }
            )

        order_key = ordering or "variant_sku"
        reverse = False
        if order_key.startswith("-"):
            reverse = True
            order_key = order_key[1:]

        allowed = {
            "variant_sku",
            "product_name",
            "warehouse_name",
            "quantity",
            "batch_count",
            "earliest_expiry",
            "cost_value",
        }
        if order_key not in allowed:
            order_key = "variant_sku"

        def _sort_key(item: dict):
            val = item.get(order_key)
            if val is None:
                return (1, "")
            return (0, val)

        rows.sort(key=_sort_key, reverse=reverse)
        return rows
