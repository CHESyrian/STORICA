"""
Accounting Phase 1 tests — CoA seed, balanced posting, idempotency, reverse.
"""

from decimal import Decimal

from django.test import TestCase

from common.exceptions.base import BusinessLogicException

from apps.accounting.models import (
    Account,
    JournalEntry,
    JournalSourceType,
)
from apps.accounting.services import ChartOfAccountsService, PostingService


class ChartOfAccountsTests(TestCase):
    def test_seed_defaults_creates_system_accounts(self):
        accounts = ChartOfAccountsService.seed_defaults()
        self.assertGreaterEqual(len(accounts), 8)
        self.assertTrue(Account.objects.filter(code="1000").exists())
        self.assertTrue(Account.objects.filter(code="4000").exists())
        cash = Account.objects.get(code="1000")
        self.assertTrue(cash.is_system)
        self.assertEqual(cash.name, "Cash")

    def test_seed_defaults_idempotent(self):
        ChartOfAccountsService.seed_defaults()
        count = Account.objects.count()
        ChartOfAccountsService.seed_defaults()
        self.assertEqual(Account.objects.count(), count)

    def test_get_by_code(self):
        ChartOfAccountsService.seed_defaults()
        ar = ChartOfAccountsService.get_by_code("1100")
        self.assertEqual(ar.name, "Accounts Receivable")


class PostingServiceTests(TestCase):
    def setUp(self):
        ChartOfAccountsService.seed_defaults()

    def test_post_balanced_entry(self):
        entry = PostingService.post(
            lines=[
                {"account": "1100", "debit": Decimal("100.00")},
                {"account": "4000", "credit": Decimal("100.00")},
            ],
            memo="Sales invoice posted",
            source_type=JournalSourceType.SALES_INVOICE,
            source_id="42",
            source_key="post",
        )
        self.assertIsNotNone(entry.pk)
        self.assertEqual(entry.lines.count(), 2)
        self.assertEqual(entry.total_debit, Decimal("100.00"))
        self.assertEqual(entry.total_credit, Decimal("100.00"))

    def test_post_rejects_unbalanced(self):
        with self.assertRaises(BusinessLogicException):
            PostingService.post(
                lines=[
                    {"account": "1100", "debit": Decimal("100.00")},
                    {"account": "4000", "credit": Decimal("90.00")},
                ],
            )

    def test_post_rejects_both_sides(self):
        with self.assertRaises(BusinessLogicException):
            PostingService.post(
                lines=[
                    {
                        "account": "1100",
                        "debit": Decimal("50.00"),
                        "credit": Decimal("50.00"),
                    },
                    {"account": "4000", "credit": Decimal("50.00")},
                ],
            )

    def test_post_idempotent_on_source(self):
        a = PostingService.post(
            lines=[
                {"account": "1010", "debit": Decimal("25.00")},
                {"account": "1100", "credit": Decimal("25.00")},
            ],
            source_type=JournalSourceType.SALES_PAYMENT,
            source_id="pay-9",
            source_key="complete",
        )
        b = PostingService.post(
            lines=[
                {"account": "1010", "debit": Decimal("25.00")},
                {"account": "1100", "credit": Decimal("25.00")},
            ],
            source_type=JournalSourceType.SALES_PAYMENT,
            source_id="pay-9",
            source_key="complete",
        )
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(JournalEntry.objects.count(), 1)

    def test_reverse_swaps_sides(self):
        original = PostingService.post(
            lines=[
                {"account": "1200", "debit": Decimal("40.00")},
                {"account": "2000", "credit": Decimal("40.00")},
            ],
            source_type=JournalSourceType.PURCHASE_INVOICE,
            source_id="inv-1",
            source_key="receive",
        )
        rev = PostingService.reverse(original)
        self.assertNotEqual(rev.pk, original.pk)
        self.assertEqual(rev.reversed_entry_id, original.pk)
        self.assertEqual(rev.total_debit, Decimal("40.00"))

        ap_line = rev.lines.get(account__code="2000")
        self.assertEqual(ap_line.debit, Decimal("40.00"))
        self.assertEqual(ap_line.credit, Decimal("0.00"))

        inv_line = rev.lines.get(account__code="1200")
        self.assertEqual(inv_line.credit, Decimal("40.00"))

    def test_reverse_idempotent(self):
        original = PostingService.post(
            lines=[
                {"account": "5000", "debit": Decimal("10.00")},
                {"account": "1200", "credit": Decimal("10.00")},
            ],
            source_type=JournalSourceType.STOCK_MOVEMENT,
            source_id="mov-1",
            source_key="complete",
        )
        r1 = PostingService.reverse(original)
        r2 = PostingService.reverse(original)
        self.assertEqual(r1.pk, r2.pk)


class LedgerEventServiceTests(TestCase):
    def setUp(self):
        ChartOfAccountsService.seed_defaults()

    def test_sales_invoice_posted_creates_ar_revenue(self):
        from types import SimpleNamespace

        from apps.accounting.services import LedgerEventService

        invoice = SimpleNamespace(pk=99, code="SI-99", total_amount=Decimal("150.00"))
        LedgerEventService.on_sales_invoice_posted(invoice)
        entry = PostingService.find_existing(
            source_type=JournalSourceType.SALES_INVOICE,
            source_id="99",
            source_key="post",
        )
        self.assertIsNotNone(entry)
        self.assertEqual(entry.total_debit, Decimal("150.00"))

    def test_sales_payment_and_refund(self):
        from types import SimpleNamespace

        from apps.accounting.services import LedgerEventService

        payment = SimpleNamespace(
            pk=7, payment_id="p7", amount=Decimal("50.00")
        )
        LedgerEventService.on_sales_payment_completed(payment)
        LedgerEventService.on_sales_payment_completed(payment)  # idempotent
        self.assertEqual(
            JournalEntry.objects.filter(
                source_type=JournalSourceType.SALES_PAYMENT,
                source_id="7",
            ).count(),
            1,
        )
        LedgerEventService.on_sales_payment_refunded(payment)
        self.assertEqual(
            JournalEntry.objects.filter(
                source_type=JournalSourceType.SALES_PAYMENT,
                source_id="7",
            ).count(),
            2,
        )


class AccountingReportServiceTests(TestCase):
    def setUp(self):
        ChartOfAccountsService.seed_defaults()
        PostingService.post(
            lines=[
                {"account": "1100", "debit": Decimal("200.00")},
                {"account": "4000", "credit": Decimal("200.00")},
            ],
            source_type=JournalSourceType.SALES_INVOICE,
            source_id="rep-1",
            source_key="post",
        )
        PostingService.post(
            lines=[
                {"account": "5000", "debit": Decimal("80.00")},
                {"account": "1200", "credit": Decimal("80.00")},
            ],
            source_type=JournalSourceType.STOCK_MOVEMENT,
            source_id="rep-m1",
            source_key="complete",
        )

    def test_trial_balance_balanced(self):
        from apps.accounting.services import AccountingReportService

        tb = AccountingReportService.trial_balance()
        self.assertTrue(tb["totals"]["balanced"])
        self.assertEqual(tb["totals"]["debit"], Decimal("280.00"))

    def test_profit_and_loss(self):
        from apps.accounting.services import AccountingReportService

        pl = AccountingReportService.profit_and_loss()
        self.assertEqual(pl["total_income"], Decimal("200.00"))
        self.assertEqual(pl["total_expense"], Decimal("80.00"))
        self.assertEqual(pl["net_profit"], Decimal("120.00"))
