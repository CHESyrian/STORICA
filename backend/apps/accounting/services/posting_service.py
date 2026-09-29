"""
PostingService — create balanced, idempotent journal entries.

Operational modules (sales, purchases, inventory) should call this
service rather than writing JournalEntry/JournalLine rows directly.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Sequence

from django.db import transaction
from django.utils import timezone

from common.exceptions.base import BusinessLogicException

from apps.accounting.models import (
    Account,
    JournalEntry,
    JournalLine,
    JournalSourceType,
)
from apps.accounting.services.chart_service import ChartOfAccountsService


class PostingService:
    """Double-entry posting with source-key idempotency."""

    @staticmethod
    def _q(amount: Decimal | int | float | str) -> Decimal:
        return Decimal(str(amount)).quantize(Decimal("0.01"))

    @staticmethod
    def find_existing(
        *,
        source_type: str,
        source_id: str,
        source_key: str = "",
    ) -> JournalEntry | None:
        if not source_id:
            return None
        return (
            JournalEntry.objects.filter(
                source_type=source_type,
                source_id=str(source_id),
                source_key=source_key or "",
            )
            .prefetch_related("lines")
            .first()
        )

    @staticmethod
    @transaction.atomic
    def post(
        *,
        lines: Sequence[dict[str, Any]],
        memo: str = "",
        entry_date=None,
        source_type: str = JournalSourceType.MANUAL,
        source_id: str = "",
        source_key: str = "",
        user=None,
        allow_duplicate: bool = False,
    ) -> JournalEntry:
        """
        Create a balanced journal entry.

        Each item in ``lines`` is a dict::

            {
                "account": Account | str account_code,
                "debit": Decimal,   # optional
                "credit": Decimal,  # optional
                "memo": str,        # optional
            }

        Exactly one of debit/credit must be > 0 per line.
        Sum(debits) must equal sum(credits) and be > 0.

        If ``source_id`` is set and an entry already exists for
        (source_type, source_id, source_key), that entry is returned
        unchanged (idempotent), unless ``allow_duplicate`` is True.
        """
        source_id = str(source_id) if source_id not in (None, "") else ""
        source_key = source_key or ""

        if source_id and not allow_duplicate:
            existing = PostingService.find_existing(
                source_type=source_type,
                source_id=source_id,
                source_key=source_key,
            )
            if existing is not None:
                return existing

        if not lines:
            raise BusinessLogicException(
                message="Journal entry requires at least one line."
            )

        normalized: list[dict[str, Any]] = []
        total_debit = Decimal("0.00")
        total_credit = Decimal("0.00")

        for raw in lines:
            account = raw.get("account")
            if isinstance(account, str):
                account = ChartOfAccountsService.get_by_code(account)
            if not isinstance(account, Account):
                raise BusinessLogicException(
                    message="Each journal line needs a valid account."
                )
            if not account.is_active:
                raise BusinessLogicException(
                    message=f"Account '{account.code}' is inactive."
                )

            debit = PostingService._q(raw.get("debit") or 0)
            credit = PostingService._q(raw.get("credit") or 0)

            if debit < 0 or credit < 0:
                raise BusinessLogicException(
                    message="Debit and credit must be non-negative."
                )
            if debit > 0 and credit > 0:
                raise BusinessLogicException(
                    message=(
                        f"Line for {account.code} cannot have both "
                        f"debit and credit."
                    )
                )
            if debit == 0 and credit == 0:
                raise BusinessLogicException(
                    message=f"Line for {account.code} has zero amount."
                )

            total_debit += debit
            total_credit += credit
            normalized.append(
                {
                    "account": account,
                    "debit": debit,
                    "credit": credit,
                    "memo": (raw.get("memo") or "")[:255],
                }
            )

        if total_debit != total_credit:
            raise BusinessLogicException(
                message=(
                    f"Journal entry is not balanced: "
                    f"debits={total_debit} credits={total_credit}."
                )
            )
        if total_debit <= 0:
            raise BusinessLogicException(
                message="Journal entry total must be greater than zero."
            )

        entry = JournalEntry.objects.create(
            entry_date=entry_date or timezone.localdate(),
            memo=(memo or "")[:255],
            source_type=source_type,
            source_id=source_id,
            source_key=source_key,
            posted_at=timezone.now(),
            created_by=user,
        )

        JournalLine.objects.bulk_create(
            [
                JournalLine(
                    entry=entry,
                    account=row["account"],
                    debit=row["debit"],
                    credit=row["credit"],
                    memo=row["memo"],
                )
                for row in normalized
            ]
        )

        return entry

    @staticmethod
    @transaction.atomic
    def reverse(
        entry: JournalEntry,
        *,
        memo: str = "",
        user=None,
        source_key: str | None = None,
    ) -> JournalEntry:
        """
        Post a reversing entry (swap debits/credits).

        Idempotent on ``source_key`` defaulting to
        ``reverse:{original_id}`` when the original has a source_id.
        """
        if entry.reversed_entry_id:
            # Someone already pointed a reverse at this entry via FK on
            # the reverse row; find it.
            existing = (
                JournalEntry.objects.filter(reversed_entry=entry)
                .order_by("id")
                .first()
            )
            if existing:
                return existing

        lines = [
            {
                "account": line.account,
                "debit": line.credit,
                "credit": line.debit,
                "memo": line.memo,
            }
            for line in entry.lines.select_related("account").all()
        ]

        rev_key = source_key
        if rev_key is None:
            rev_key = f"reverse:{entry.pk}"

        reverse_entry = PostingService.post(
            lines=lines,
            memo=memo or f"Reversal of JE#{entry.pk}",
            entry_date=timezone.localdate(),
            source_type=entry.source_type,
            source_id=entry.source_id or str(entry.pk),
            source_key=rev_key,
            user=user,
        )
        if reverse_entry.reversed_entry_id != entry.pk:
            reverse_entry.reversed_entry = entry
            reverse_entry.save(update_fields=["reversed_entry"])
        return reverse_entry
