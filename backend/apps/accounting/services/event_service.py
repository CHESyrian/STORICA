"""
Ledger event bridge — map operational events to journal posts.

Called from sales / purchases / inventory services after the business
transaction succeeds. All posts are idempotent on source keys so
retries and re-entrant paths are safe.
"""

from __future__ import annotations

import logging
from decimal import Decimal

from apps.accounting.models import JournalSourceType
from apps.accounting.services.chart_service import ChartOfAccountsService
from apps.accounting.services.posting_service import PostingService

logger = logging.getLogger(__name__)

# Account codes (must match ChartOfAccountsService defaults)
CASH = "1000"
BANK = "1010"
AR = "1100"
INVENTORY = "1200"
AP = "2000"
REVENUE = "4000"
COGS = "5000"
INV_ADJ = "5100"


def _ensure_coa() -> None:
    ChartOfAccountsService.seed_defaults()


def _q(amount) -> Decimal:
    return Decimal(str(amount or 0)).quantize(Decimal("0.01"))


class LedgerEventService:
    """Thin wrappers around PostingService for domain events."""

    # ------------------------------------------------------------------
    # Sales
    # ------------------------------------------------------------------

    @staticmethod
    def on_sales_invoice_posted(invoice, user=None) -> None:
        """DR AR / CR Revenue for invoice total."""
        amount = _q(invoice.total_amount)
        if amount <= 0:
            return
        _ensure_coa()
        PostingService.post(
            lines=[
                {"account": AR, "debit": amount},
                {"account": REVENUE, "credit": amount},
            ],
            memo=f"Sales invoice {getattr(invoice, 'code', invoice.pk)} posted",
            source_type=JournalSourceType.SALES_INVOICE,
            source_id=str(invoice.pk),
            source_key="post",
            user=user,
        )

    @staticmethod
    def on_sales_invoice_cancelled(invoice, user=None) -> None:
        """Reverse the post entry if it exists."""
        _ensure_coa()
        existing = PostingService.find_existing(
            source_type=JournalSourceType.SALES_INVOICE,
            source_id=str(invoice.pk),
            source_key="post",
        )
        if existing:
            PostingService.reverse(existing, user=user)

    @staticmethod
    def on_sales_payment_completed(payment, user=None) -> None:
        """DR Cash / CR AR for payment amount."""
        amount = _q(payment.amount)
        if amount <= 0:
            return
        _ensure_coa()
        PostingService.post(
            lines=[
                {"account": CASH, "debit": amount},
                {"account": AR, "credit": amount},
            ],
            memo=(
                f"Sales payment {getattr(payment, 'payment_id', payment.pk)}"
            ),
            source_type=JournalSourceType.SALES_PAYMENT,
            source_id=str(payment.pk),
            source_key="complete",
            user=user,
        )

    @staticmethod
    def on_sales_payment_refunded(payment, user=None) -> None:
        _ensure_coa()
        existing = PostingService.find_existing(
            source_type=JournalSourceType.SALES_PAYMENT,
            source_id=str(payment.pk),
            source_key="complete",
        )
        if existing:
            PostingService.reverse(existing, user=user)

    # ------------------------------------------------------------------
    # Purchases
    # ------------------------------------------------------------------

    @staticmethod
    def on_purchase_invoice_received(invoice, user=None) -> None:
        """DR Inventory / CR AP for purchase invoice total (cost)."""
        amount = _q(invoice.total_amount)
        if amount <= 0:
            return
        _ensure_coa()
        PostingService.post(
            lines=[
                {"account": INVENTORY, "debit": amount},
                {"account": AP, "credit": amount},
            ],
            memo=(
                f"Purchase invoice {getattr(invoice, 'code', invoice.pk)} "
                f"received"
            ),
            source_type=JournalSourceType.PURCHASE_INVOICE,
            source_id=str(invoice.pk),
            source_key="receive",
            user=user,
        )

    @staticmethod
    def on_purchase_invoice_cancelled(invoice, user=None) -> None:
        _ensure_coa()
        existing = PostingService.find_existing(
            source_type=JournalSourceType.PURCHASE_INVOICE,
            source_id=str(invoice.pk),
            source_key="receive",
        )
        if existing:
            PostingService.reverse(existing, user=user)

    @staticmethod
    def on_purchase_payment_completed(payment, user=None) -> None:
        """DR AP / CR Cash for payment amount."""
        amount = _q(payment.amount)
        if amount <= 0:
            return
        _ensure_coa()
        PostingService.post(
            lines=[
                {"account": AP, "debit": amount},
                {"account": CASH, "credit": amount},
            ],
            memo=(
                f"Purchase payment "
                f"{getattr(payment, 'payment_id', payment.pk)}"
            ),
            source_type=JournalSourceType.PURCHASE_PAYMENT,
            source_id=str(payment.pk),
            source_key="complete",
            user=user,
        )

    @staticmethod
    def on_purchase_payment_refunded(payment, user=None) -> None:
        _ensure_coa()
        existing = PostingService.find_existing(
            source_type=JournalSourceType.PURCHASE_PAYMENT,
            source_id=str(payment.pk),
            source_key="complete",
        )
        if existing:
            PostingService.reverse(existing, user=user)

    # ------------------------------------------------------------------
    # Inventory movements
    # ------------------------------------------------------------------

    @staticmethod
    def on_stock_movement_completed(movement, user=None) -> None:
        """
        Post cost impact for COMPLETED movements.

        OUT / sold stock: DR COGS / CR Inventory (batch cost × qty).
        ADJUSTMENT decreases: same as COGS path via Inventory Adjustment.
        IN from purchases is posted at purchase-invoice receive; skip
        plain IN to avoid double-counting when reference is a purchase.
        """
        from common.models.choices import StockMovementType

        qty = _q(movement.quantity)
        if qty <= 0:
            return

        cost_unit = Decimal("0")
        batch = getattr(movement, "batch", None)
        if batch is not None and getattr(batch, "cost_price", None) is not None:
            cost_unit = _q(batch.cost_price)
        else:
            # Fall back to movement unit_price when no batch cost
            cost_unit = _q(getattr(movement, "unit_price", 0))

        amount = (qty * cost_unit).quantize(Decimal("0.01"))
        if amount <= 0:
            return

        mtype = movement.movement_type
        _ensure_coa()
        sid = str(movement.pk)

        if mtype == StockMovementType.OUT:
            PostingService.post(
                lines=[
                    {"account": COGS, "debit": amount},
                    {"account": INVENTORY, "credit": amount},
                ],
                memo=f"Stock OUT movement {sid}",
                source_type=JournalSourceType.STOCK_MOVEMENT,
                source_id=sid,
                source_key="complete",
                user=user,
            )
        elif mtype == StockMovementType.ADJUSTMENT:
            # Treat as expense write-off of inventory cost
            PostingService.post(
                lines=[
                    {"account": INV_ADJ, "debit": amount},
                    {"account": INVENTORY, "credit": amount},
                ],
                memo=f"Stock ADJUSTMENT movement {sid}",
                source_type=JournalSourceType.STOCK_MOVEMENT,
                source_id=sid,
                source_key="complete",
                user=user,
            )
        elif mtype == StockMovementType.RETURN:
            # Customer return increases inventory, reduces COGS
            PostingService.post(
                lines=[
                    {"account": INVENTORY, "debit": amount},
                    {"account": COGS, "credit": amount},
                ],
                memo=f"Stock RETURN movement {sid}",
                source_type=JournalSourceType.STOCK_MOVEMENT,
                source_id=sid,
                source_key="complete",
                user=user,
            )
        # IN / TRANSFER: no ledger here (purchase IN posted on invoice;
        # transfer is warehouse-only).
