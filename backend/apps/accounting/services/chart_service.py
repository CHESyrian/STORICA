"""
Chart of accounts — seed and lookup helpers.
"""

from __future__ import annotations

from django.db import transaction

from apps.accounting.models import Account, AccountType


# Default STORICA chart. Codes are stable posting-rule keys.
DEFAULT_ACCOUNTS: list[dict] = [
    {
        "code": "1000",
        "name": "Cash",
        "account_type": AccountType.ASSET,
        "description": "Cash on hand and petty cash.",
    },
    {
        "code": "1010",
        "name": "Bank",
        "account_type": AccountType.ASSET,
        "description": "Bank and electronic payment accounts.",
    },
    {
        "code": "1100",
        "name": "Accounts Receivable",
        "account_type": AccountType.ASSET,
        "description": "Amounts owed by customers.",
    },
    {
        "code": "1200",
        "name": "Inventory",
        "account_type": AccountType.ASSET,
        "description": "Inventory at cost (not quantities).",
    },
    {
        "code": "2000",
        "name": "Accounts Payable",
        "account_type": AccountType.LIABILITY,
        "description": "Amounts owed to suppliers.",
    },
    {
        "code": "3000",
        "name": "Owner Equity",
        "account_type": AccountType.EQUITY,
        "description": "Owner equity / retained earnings placeholder.",
    },
    {
        "code": "4000",
        "name": "Sales Revenue",
        "account_type": AccountType.INCOME,
        "description": "Revenue from sales invoices.",
    },
    {
        "code": "5000",
        "name": "Cost of Goods Sold",
        "account_type": AccountType.EXPENSE,
        "description": "Cost of inventory sold (FIFO cost).",
    },
    {
        "code": "5100",
        "name": "Inventory Adjustment",
        "account_type": AccountType.EXPENSE,
        "description": "Stock adjustments and shrinkage.",
    },
]


class ChartOfAccountsService:
    """Seed and resolve system accounts."""

    @staticmethod
    @transaction.atomic
    def seed_defaults(*, force: bool = False) -> list[Account]:
        """
        Ensure default system accounts exist.

        Idempotent: existing codes are left unchanged unless ``force``
        updates name/type/description on system rows.
        """
        created_or_existing: list[Account] = []
        for spec in DEFAULT_ACCOUNTS:
            account, created = Account.objects.get_or_create(
                code=spec["code"],
                defaults={
                    "name": spec["name"],
                    "account_type": spec["account_type"],
                    "description": spec.get("description", ""),
                    "is_system": True,
                    "is_active": True,
                },
            )
            if not created and force and account.is_system:
                account.name = spec["name"]
                account.account_type = spec["account_type"]
                account.description = spec.get("description", "")
                account.is_active = True
                account.save(
                    update_fields=[
                        "name",
                        "account_type",
                        "description",
                        "is_active",
                        "updated_at",
                    ]
                )
            created_or_existing.append(account)
        return created_or_existing

    @staticmethod
    def get_by_code(code: str) -> Account:
        from common.exceptions.base import NotFoundException

        try:
            return Account.objects.get(code=code, is_active=True)
        except Account.DoesNotExist as exc:
            raise NotFoundException(
                message=f"Account with code '{code}' not found or inactive."
            ) from exc
