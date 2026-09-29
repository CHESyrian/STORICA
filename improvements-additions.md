## Completion backlog by section

Priority: **P0** = blocks real use · **P1** = needed for a finished module · **P2** = polish / advanced · **P3** = nice-to-have.

---

### Inventory (~92%)

| Item | Type | Priority | Notes |
|------|------|----------|-------|
| Expiry / near-expiry alerts on stock status | Add | P1 | Batches have expiry; no dedicated filter/UI highlight beyond generic status |
| Batch merge / split / write-off workflow | Add | P2 | Adjustments exist; no guided batch ops |
| Multi-warehouse transfer UI polish | Improve | P2 | TRANSFER works in API/tests; ensure dialog always requires dest warehouse clearly |
| Reorder suggestions from `min_stock` | Add | P2 | Low-stock flag exists; no “suggested PO” action |
| Serial/lot tracking beyond batch | Add | P3 | Out of current design |
| Inventory valuation report data API | Add | P2 | Needed by Panel reports |

---

### Sales (~88%)

| Item | Type | Priority | Notes |
|------|------|----------|-------|
| Payment **refund** (API + UI) | Add | P1 | Purchases has refund; sales does not |
| Order **complete** button in UI | Add | P1 | API exists; only confirm/cancel wired |
| Invoice PDF / print | Add | P1 | No document output |
| Overdue invoice status job / flag | Add | P2 | `OVERDUE` in choices; not driven by dates |
| Partial ship / multi-invoice per order | Add | P2 | One invoice per order today |
| Credit notes / returns linked to sales | Add | P2 | Inventory RETURN exists; not tied to sales docs |
| Sales payment list filters (customer/invoice) | Improve | P2 | Basic list/view only |
| Stronger concurrency tests on post | Improve | P2 | Basic post tests exist |
| Customer credit limit / balance | Add | P3 | — |

---

### Purchases (~90%)

| Item | Type | Priority | Notes |
|------|------|----------|-------|
| Optional **draft** invoice (receive later) | Add | P1 | Today stock always receives on create |
| Order **complete** button in UI | Add | P1 | API exists; confirm/cancel only in UI |
| Refund action on Payments tab | Add | P1 | API exists; UI not wired |
| Invoice PDF / print | Add | P1 | Same gap as sales |
| Partial receive (multi-invoice per PO) | Add | P2 | One invoice per order enforced |
| Landed cost / extra charges on invoice | Add | P2 | — |
| Supplier performance metrics | Add | P3 | — |
| Clearer “received on create” status label in UI | Improve | P2 | Avoid confusion with sales “Post” |

---

### Users / Auth (~85%)

| Item | Type | Priority | Notes |
|------|------|----------|-------|
| UI for **sessions** list / revoke own session | Add | P1 | API exists; limited desktop surface |
| Role permission matrix in UI (what each role can do) | Add | P2 | Backend ranks exist; not explained in app |
| Password policy / complexity rules | Improve | P2 | Basic change/reset only |
| 2FA / SSO | Add | P3 | — |
| Fine-grained per-resource permissions | Add | P3 | Role ranks are coarse |
| Audit log viewer (logins + critical actions) | Add | P2 | Login history API for admin; no full audit UI |

---

### Panel (~70%)

| Item | Type | Priority | Notes |
|------|------|----------|-------|
| Real **report backends** (inventory, movements, sales, …) | Add | P0 | Tabs open with info stubs only |
| Date range / warehouse / category filters on reports | Add | P1 | — |
| Export CSV/PDF from report tabs | Add | P1 | — |
| Dashboard KPIs (stock value, open orders, low stock count) | Add | P1 | Quick-create only today |
| Purchases report button parity | Add | P2 | Sales-oriented set is stronger |
| Remove or merge duplicate `panel_tab2` | Improve | P2 | Cleanup |
| Wire quick-create to same dialogs as main modules | Improve | P1 | Ensure parity and refresh after create |

---

### Accounting (~5%)

| Item | Type | Priority | Notes |
|------|------|----------|-------|
| Enable app + chart of accounts | Add | P0 | Commented out of `INSTALLED_APPS` |
| Journal entries from sales/purchase postings | Add | P0 | Core integration |
| AR / AP ledgers linked to invoices & payments | Add | P0 | — |
| Tax configuration (rates, inclusive/exclusive) | Add | P1 | Rates on lines only today |
| Period close / fiscal year | Add | P1 | — |
| Financial statements (P&amp;L, balance sheet trial) | Add | P1 | — |
| Models, services, serializers, views, tests, UI | Add | P0 | Stub package only |
| Desktop Accounting section | Add | P1 | No frontend module |

---

### Cross-cutting / platform

| Item | Type | Priority | Notes |
|------|------|----------|-------|
| Automated CI test run (Postgres) | Add | P1 | `run_tests.py` exists; env-dependent |
| API integration tests for new actions | Improve | P1 | Service tests stronger than HTTP tests |
| Optimistic UI refresh after cancel/post across tabs | Improve | P2 | e.g. stock status after sales post |
| i18n / multi-currency | Add | P3 | — |
| Backup / restore guidance | Add | P3 | — |
| End-to-end desktop tests | Add | P2 | None today |

---

### Suggested order to “complete” the product

1. **Panel reports + KPI dashboard** (makes the app feel finished for managers)  
2. **Sales refund + order complete UI** (parity with purchases)  
3. **Purchases draft/receive-later option** (if operations need it)  
4. **Document print/PDF** for invoices  
5. **Accounting foundation** (only when the trade loop is stable)  

Core **Inventory / Sales / Purchases** operational loops are largely complete; remaining work is **documents, refunds/UI parity, reports, and accounting**.