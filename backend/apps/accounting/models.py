"""
Accounting models — chart of accounts and double-entry journal.

Inventory quantities stay in apps.inventory. This app records monetary
effects only (and inventory cost amounts when callers supply them).
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class AccountType(models.TextChoices):
    ASSET = "asset", "Asset"
    LIABILITY = "liability", "Liability"
    EQUITY = "equity", "Equity"
    INCOME = "income", "Income"
    EXPENSE = "expense", "Expense"


class JournalSourceType(models.TextChoices):
    """Operational document that produced a journal entry."""

    MANUAL = "manual", "Manual"
    SALES_INVOICE = "sales_invoice", "Sales invoice"
    SALES_PAYMENT = "sales_payment", "Sales payment"
    PURCHASE_INVOICE = "purchase_invoice", "Purchase invoice"
    PURCHASE_PAYMENT = "purchase_payment", "Purchase payment"
    STOCK_MOVEMENT = "stock_movement", "Stock movement"


class Account(models.Model):
    """
    Chart-of-accounts node.

    ``code`` is stable and used by posting rules (e.g. ``1000`` Cash).
    """

    code = models.CharField(max_length=20, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
    )
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(
        default=False,
        help_text="Seeded system account; protect from casual delete.",
    )
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["account_type", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} — {self.name}"


class JournalEntry(models.Model):
    """
    Header for a balanced set of journal lines.

    ``source_type`` + ``source_id`` + ``source_key`` support idempotent
    posting from operational modules (same event -> same entry).
    """

    entry_date = models.DateField(default=timezone.localdate)
    memo = models.CharField(max_length=255, blank=True)

    source_type = models.CharField(
        max_length=40,
        choices=JournalSourceType.choices,
        default=JournalSourceType.MANUAL,
        db_index=True,
    )
    source_id = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="PK or UUID string of the source document.",
    )
    source_key = models.CharField(
        max_length=80,
        blank=True,
        default="",
        help_text=(
            "Optional discriminator when one document yields several "
            "entries (e.g. 'post', 'refund')."
        ),
    )

    posted_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="journal_entries_created",
    )
    reversed_entry = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reversals",
        help_text="If set, this entry reverses the linked original.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-entry_date", "-id"]
        indexes = [
            models.Index(fields=["source_type", "source_id"]),
            models.Index(fields=["entry_date"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["source_type", "source_id", "source_key"],
                condition=~models.Q(source_id=""),
                name="accounting_journal_source_unique",
            ),
        ]

    def __str__(self) -> str:
        return f"JE#{self.pk} {self.entry_date} ({self.source_type})"

    @property
    def total_debit(self) -> Decimal:
        return self.lines.aggregate(
            t=models.Sum("debit")
        )["t"] or Decimal("0")

    @property
    def total_credit(self) -> Decimal:
        return self.lines.aggregate(
            t=models.Sum("credit")
        )["t"] or Decimal("0")


class JournalLine(models.Model):
    """Single debit or credit line (exactly one side non-zero)."""

    entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name="lines",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="journal_lines",
    )
    memo = models.CharField(max_length=255, blank=True)
    debit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    credit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
    )

    class Meta:
        ordering = ["id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(debit__gte=0) & models.Q(credit__gte=0),
                name="accounting_line_non_negative",
            ),
            models.CheckConstraint(
                condition=(
                    (models.Q(debit__gt=0) & models.Q(credit=0))
                    | (models.Q(credit__gt=0) & models.Q(debit=0))
                ),
                name="accounting_line_one_side_only",
            ),
        ]

    def __str__(self) -> str:
        side = f"DR {self.debit}" if self.debit else f"CR {self.credit}"
        return f"{self.account.code} {side}"

    def clean(self) -> None:
        if self.debit and self.credit:
            raise ValidationError(
                "A journal line cannot have both debit and credit."
            )
        if not self.debit and not self.credit:
            raise ValidationError(
                "A journal line must have a debit or a credit."
            )
