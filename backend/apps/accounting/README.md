# Accounting

Double-entry ledger for STORICA. Inventory quantities stay in
`apps.inventory`; this app records **monetary** effects and inventory
**cost** amounts supplied by callers.

## Status

| Phase | Item | State |
|-------|------|--------|
| 1 | Models / CoA / PostingService | Done |
| 2 | Event hooks (sales, purchases, stock) | Done |
| 3 | Trial balance / P&L API + Panel | Done |

## Event hooks (Phase 2)

| Event | Journal |
|-------|---------|
| Sales invoice posted | DR AR / CR Revenue |
| Sales invoice cancelled (was posted) | Reverse post |
| Sales payment completed | DR Cash / CR AR |
| Sales payment refunded | Reverse payment |
| Purchase invoice received | DR Inventory / CR AP |
| Purchase invoice cancelled | Reverse receive |
| Purchase payment completed/partial | DR AP / CR Cash |
| Purchase payment refunded | Reverse payment |
| Stock OUT completed | DR COGS / CR Inventory |
| Stock ADJUSTMENT completed | DR Inv. Adj / CR Inventory |
| Stock RETURN completed | DR Inventory / CR COGS |

All posts are **idempotent** on `(source_type, source_id, source_key)`.

## API (Phase 3)

```
GET  /api/accounting/trial-balance/?as_of=YYYY-MM-DD
GET  /api/accounting/profit-loss/?from=YYYY-MM-DD&to=YYYY-MM-DD
GET  /api/accounting/accounts/
POST /api/accounting/seed-coa/
```

## Default chart of accounts

| Code | Name | Type |
|------|------|------|
| 1000 | Cash | asset |
| 1010 | Bank | asset |
| 1100 | Accounts Receivable | asset |
| 1200 | Inventory | asset |
| 2000 | Accounts Payable | liability |
| 3000 | Owner Equity | equity |
| 4000 | Sales Revenue | income |
| 5000 | Cost of Goods Sold | expense |
| 5100 | Inventory Adjustment | expense |

```bash
python manage.py migrate accounting
python run_tests.py apps.accounting
python manage.py shell -c "from apps.accounting.services import ChartOfAccountsService; ChartOfAccountsService.seed_defaults()"
```
