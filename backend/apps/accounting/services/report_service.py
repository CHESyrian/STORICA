"""
Accounting read models — trial balance and simple P&L.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from django.db.models import Sum, Q
from django.utils import timezone

from apps.accounting.models import Account, AccountType, JournalLine
from apps.accounting.services.chart_service import ChartOfAccountsService


def _q(value) -> Decimal:
    return Decimal(str(value or 0)).quantize(Decimal("0.01"))


class AccountingReportService:
    """Aggregate journal lines into report rows."""

    @staticmethod
    def trial_balance(*, as_of: date | None = None) -> dict:
        """
        Return trial balance as of ``as_of`` (inclusive).

        Each account: total debit, total credit, and net balance
        (debit-normal for asset/expense, credit-normal for liability/
        equity/income — reported as signed ``balance`` where positive
        means the natural side).
        """
        ChartOfAccountsService.seed_defaults()
        as_of = as_of or timezone.localdate()

        qs = JournalLine.objects.filter(
            entry__entry_date__lte=as_of,
        ).values(
            "account_id",
            "account__code",
            "account__name",
            "account__account_type",
        ).annotate(
            total_debit=Sum("debit"),
            total_credit=Sum("credit"),
        ).order_by("account__code")

        rows = []
        sum_debit = Decimal("0.00")
        sum_credit = Decimal("0.00")

        for row in qs:
            td = _q(row["total_debit"])
            tc = _q(row["total_credit"])
            atype = row["account__account_type"]
            if atype in {AccountType.ASSET, AccountType.EXPENSE}:
                balance = td - tc
            else:
                balance = tc - td
            rows.append(
                {
                    "account_id": row["account_id"],
                    "code": row["account__code"],
                    "name": row["account__name"],
                    "account_type": atype,
                    "debit": td,
                    "credit": tc,
                    "balance": balance,
                }
            )
            sum_debit += td
            sum_credit += tc

        # Include active accounts with zero activity
        seen = {r["account_id"] for r in rows}
        for acc in Account.objects.filter(is_active=True).order_by("code"):
            if acc.pk in seen:
                continue
            rows.append(
                {
                    "account_id": acc.pk,
                    "code": acc.code,
                    "name": acc.name,
                    "account_type": acc.account_type,
                    "debit": Decimal("0.00"),
                    "credit": Decimal("0.00"),
                    "balance": Decimal("0.00"),
                }
            )
        rows.sort(key=lambda r: r["code"])

        return {
            "as_of": as_of.isoformat(),
            "rows": rows,
            "totals": {
                "debit": sum_debit,
                "credit": sum_credit,
                "balanced": sum_debit == sum_credit,
            },
        }

    @staticmethod
    def profit_and_loss(
        *,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> dict:
        """
        Simple P&amp;L: income and expense accounts between dates inclusive.
        """
        ChartOfAccountsService.seed_defaults()
        date_to = date_to or timezone.localdate()
        if date_from is None:
            date_from = date(date_to.year, 1, 1)

        filt = Q(
            entry__entry_date__gte=date_from,
            entry__entry_date__lte=date_to,
        )

        def _side(account_type: str) -> list[dict]:
            qs = (
                JournalLine.objects.filter(
                    filt,
                    account__account_type=account_type,
                )
                .values(
                    "account_id",
                    "account__code",
                    "account__name",
                )
                .annotate(
                    total_debit=Sum("debit"),
                    total_credit=Sum("credit"),
                )
                .order_by("account__code")
            )
            out = []
            for row in qs:
                td = _q(row["total_debit"])
                tc = _q(row["total_credit"])
                if account_type == AccountType.INCOME:
                    amount = tc - td
                else:
                    amount = td - tc
                if amount == 0:
                    continue
                out.append(
                    {
                        "account_id": row["account_id"],
                        "code": row["account__code"],
                        "name": row["account__name"],
                        "amount": amount,
                    }
                )
            return out

        income = _side(AccountType.INCOME)
        expense = _side(AccountType.EXPENSE)
        total_income = sum((r["amount"] for r in income), Decimal("0.00"))
        total_expense = sum((r["amount"] for r in expense), Decimal("0.00"))

        return {
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "income": income,
            "expense": expense,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_profit": total_income - total_expense,
        }
