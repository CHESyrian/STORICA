# STORICA

**Professional Point-of-Sale & Inventory Management Desktop Application**

STORICA is a full-stack business system: a **Django 6 + DRF** REST API backend and a native **PyQt6** desktop client. It covers inventory (products, variants, batches, warehouses, stock movements, stock status), sales (customers, orders, invoices, payments), purchases (suppliers, orders, invoices, payments), role-based user management with login audit and sessions, and a Panel for quick-create actions and report workspaces.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  STORICA Desktop (PyQt6)                                    │
│  frontend/                                                  │
│    api/          AuthClient, workers, JWT handling          │
│    services/     Inventory / Sales / Purchases / General    │
│    controllers/  UI ↔ service glue                          │
│    ui/           MainWindow, Sidebar, tabs, dialogs         │
│    utils/        Config, AuthManager, Theme, Logging        │
└────────────────────────────┬────────────────────────────────┘
                             │  HTTP + JWT
                             ▼
┌─────────────────────────────────────────────────────────────┐
│  Django 6 + DRF Backend                                     │
│  backend/                                                   │
│    apps/                                                    │
│      inventory/   Warehouse, Category, Product, Variant,    │
│                   Batch, StockMovement, StockStatus         │
│      sales/       Customer, SalesOrder, SalesInvoice,       │
│                   SalesPayment                              │
│      purchases/   Supplier, PurchasesOrder/Invoice/Payment  │
│      users/       Custom User, sessions, login history      │
│      accounting/  (stub — see apps/accounting/README.md)    │
│    common/        ApiResponse, RolePermission, exceptions,  │
│                   pagination, generators, validators        │
│    config/        settings, urls, api_router                │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                       PostgreSQL
```

**Key design decisions**

- **Batch.quantity** is the source of truth for stock per warehouse.
- **Variant.quantity** is a denormalized total kept in sync by inventory services under `select_for_update`.
- **Variant.min_stock** is the reorder threshold; stock status flags rows when on-hand ≤ min stock.
- Stock movements are created as `PENDING` and only mutate quantities when transitioned to `COMPLETED`.
- Sales **post invoice** allocates stock **FIFO** via `BatchService.allocate_fifo` and creates completed OUT movements.
- Purchase invoices **receive stock on create** (batches are created/updated automatically; `post_invoice` is idempotent).
- Role hierarchy: `guest` < `viewer` < `user` < `manager` < `admin` (plus Django superuser).

---

## Requirements

### Backend

- Python 3.12+
- PostgreSQL 14+
- Redis (optional, for caching)

### Frontend

- Python 3.12+
- PyQt6

---

## Backend Setup

```bash
cd backend

# 1. Create virtualenv & install
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Environment
# Edit backend/.env (or copy from a template). Required variables:
#   SECRET_KEY=...
#   DEBUG=True
#   ALLOWED_HOSTS=localhost,127.0.0.1
#   DB_NAME=storica_db
#   DB_USER=sm_admin
#   DB_PASSWORD=sm_password
#   DB_HOST=localhost
#   DB_PORT=5432
#   JWT_SECRET_KEY=...             # optional override

# 3. Database
createdb storica_db                # or use your preferred method
python manage.py migrate
python manage.py createsuperuser

# 4. Run
python manage.py runserver
# API:          http://127.0.0.1:8000/api/
# Schema:       http://127.0.0.1:8000/api/schema/
# Scalar docs:  http://127.0.0.1:8000/api/docs/
# Admin:        http://127.0.0.1:8000/admin/
```

### JWT & auth endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/token/` | Login (custom view: records history, session, IP/UA; lockout after failed attempts) |
| POST | `/api/token/refresh/` | Refresh access token |
| POST | `/api/token/verify/` | Verify access token |
| GET | `/api/auth/me/` | Current user profile + permissions |
| PUT/PATCH | `/api/auth/me/update/` | Update own profile (email, name, theme, language) |
| POST | `/api/auth/me/change-password/` | Change own password |
| GET | `/api/auth/me/sessions/` | List own active sessions |
| POST | `/api/auth/logout/` | Blacklist refresh token + deactivate session |
| GET/POST | `/api/auth/` | Admin: list / create users |
| PATCH | `/api/auth/{id}/` | Admin: update user (role, active, …) |
| DELETE | `/api/auth/{id}/` | Admin: deactivate user |
| POST | `/api/auth/{id}/reset-password/` | Admin: reset password (revokes sessions) |
| POST | `/api/auth/{id}/revoke-sessions/` | Admin: revoke all sessions |
| GET | `/api/auth/{id}/login-history/` | Admin: recent login history |

### Main resource routes

Registered in `config/api_router.py`:

| Prefix | Description |
|--------|-------------|
| `warehouses`, `categories`, `products`, `variants`, `batches` | Core inventory entities |
| `stock-movements` | Stock movement lifecycle (PENDING → COMPLETED) |
| `stock-status` | Aggregated on-hand stock by variant × warehouse |
| `customers`, `sales-orders`, `sales-invoices`, `sales-payments` | Sales |
| `suppliers`, `purchases-orders`, `purchases-invoices`, `purchases-payments` | Purchases |
| `auth` | Users and session management |

**Stock status** (`GET /api/stock-status/`, `GET /api/stock-status/all/`):

- Aggregates active batches by variant and warehouse
- Returns quantity, batch count, earliest expiry, cost value, `min_stock`, `is_low_stock`
- Query params: `search`, `warehouse`, `category`, `product`, `variant`, `is_active`, `zero_stock`, `low_stock`, `ordering`

---

## Frontend Setup

```bash
# From project root
python -m venv .venv
source .venv/bin/activate
pip install -r frontend/requirements.txt
pip install -r backend/requirements.txt   # if you also develop the API

# Configure API base URL (see Configuration below)
# Then launch:
python run.py
```

### Configuration

`frontend/utils/config.py` contains the default:

```python
API_BASE_URL = "http://localhost:8000/api"
```

Override with the `STORICA_API_BASE_URL` environment variable when needed. Session tokens are stored encrypted under `~/.storica/` with machine-ID binding and atomic writes (`AuthManager`).

### Desktop modules

| Section | Contents |
|---------|----------|
| Inventory | Categories, products, variants, warehouses, batches (read-only list), stock movements (create + complete), stock status (low-stock highlight & filter) |
| Sales | Customers, orders (confirm/cancel), invoices (post / cancel / add payment), payments (list/view only) |
| Purchases | Suppliers, orders (confirm/cancel), invoices (receive-on-create, cancel reverses stock, add payment), payments |
| Users | Admin user list/create/edit/deactivate, password reset (admin role) |
| Panel | Quick-create shortcuts; report buttons open **closable report tabs** in PanelView |

### UI conventions

- **No application menu bar** — About is available from the **sidebar footer** (About STORICA, above Logout).
- **Batches** are not created manually in the Batches tab; they are created/updated when a **purchase invoice** is posted/received.
- **Sales payments** are recorded from the **Sales Invoices** tab (select invoice → Add payment) and are marked **completed** immediately. The Payments tab is list/view only.
- **Sales invoices**: create from an order, **Post** a draft to allocate stock FIFO, **Cancel** draft or unpaid sent (reverses stock if posted).
- **Sales orders**: **Confirm** draft → confirmed; **Cancel** draft/confirmed/processing; complete via service when processing/shipped/delivered.
- **Purchase invoices receive stock on create** (batches + IN movements). There is no separate Post step that moves stock. **Cancel** unpaid invoices reverses received stock.
- **Purchase orders**: **Confirm** draft; **Cancel** draft/confirmed/processing.
- **Stock movements**: create as PENDING, then **Complete** from the Stock Movements tab to apply quantity changes.
- **Stock Status**: low-stock rows are colour-highlighted; the reusable navbar **flag** checkbox is labeled “Low stock only” on this tab and filters via `low_stock=true`.
- **Panel reports**: each report opens (or focuses) a closable workspace tab instead of a dialog.

---

## Authentication & Authorization

1. **Login** — Desktop client posts username/password to `/api/token/`.
2. **Audit** — Successful logins write `UserLoginHistory` and `UserSession`; failures are recorded (lockout after 5 failed attempts in 15 minutes for known users).
3. **Tokens** — Access + refresh JWTs. Optional “Remember me” encrypts them locally (Fernet + machine binding).
4. **Auto-login** — On startup the client loads saved tokens, refreshes if needed, and verifies.
5. **Roles** (`apps.users.models.UserRole`):

   | Role | Typical capabilities |
   |------|----------------------|
   | admin | Full access (`is_superuser` / `is_staff` as needed) |
   | manager | Read + write + approve + limited user management |
   | user | Read + write on operational data |
   | viewer | Read only |
   | guest | Minimal authenticated access |

Enforcement uses `common.permissions.RolePermission` (and helpers such as `IsAdminRole`, `IsManagerOrAbove`). ViewSets can override `read_roles`, `write_roles`, `delete_roles`, `approve_roles`. UI permission strings from `/api/auth/me/` are derived from the same role ranks via `UserService.permissions_for_user`.

Business logic for users lives in `apps.users.services.UserService` (create/update, password reset, sessions, lockout).

---

## Stock & Inventory Rules

| Rule | Detail |
|------|--------|
| Source of truth | `Batch.quantity` (per warehouse). `Variant.quantity` is denormalized. |
| Min stock | `Variant.min_stock` reorder threshold; stock status sets `is_low_stock` when qty ≤ min and min > 0. |
| Lifecycle | Create movement → `PENDING`. Transition to `COMPLETED` applies quantity change under `select_for_update`. |
| Negative stock | Forbidden. Validated on create (OUT/TRANSFER) and again on complete. |
| Concurrent safety | `select_for_update()` on movement, batch, and variant rows. |
| No batch | Movements without a batch cannot be completed (`BusinessLogicException`). |
| TRANSFER | Completes with source decrease and destination batch increase; variant total stays stable. |
| ADJUSTMENT | Sets batch quantity to the movement quantity (absolute); variant total adjusts by the delta. |
| RETURN | Increases batch and variant quantity (same direction as IN). |
| Sales post invoice | FIFO allocation per line; creates completed OUT movements. |
| Purchase receiving | Stock applied on invoice **create** (batches auto-created/updated); `post_invoice` is idempotent. |

Supported movement types: `IN`, `OUT`, `TRANSFER`, `ADJUSTMENT`, `RETURN`.

---

## Testing

```bash
cd backend

# Recommended: verbose runner with timing summary
python run_tests.py
python run_tests.py apps.inventory          # one app
python run_tests.py --keepdb                # reuse test DB (faster re-runs)
python run_tests.py --failfast

# Or Django defaults (use -v 2 to see each test name as it runs)
python manage.py test -v 2
python manage.py test apps.inventory.tests -v 2 --keepdb
python manage.py test apps.sales.tests apps.purchases.tests apps.users.tests -v 2
```

`-v 2` prints each test as it starts/finishes. `run_tests.py` wraps the same runner and prints labels, verbosity, and total elapsed time. `--keepdb` avoids rebuilding the test database on every run.

**Coverage includes:**

- Inventory: stock movement lifecycle (IN/OUT/TRANSFER/ADJUSTMENT/RETURN), oversell protection, stock status aggregation, `min_stock` / low-stock flags
- Sales: order → invoice → payment happy path; post FIFO; cancel invoice (stock reverse); order confirm/complete; payment completed-on-create
- Purchases: receive-on-create (batch/stock); cancel invoice reverses stock; payment optional order + refund; order confirm/complete
- Users: role hierarchy / `RolePermission`, auth API (login history, me, admin create, password change, logout)

---

## Project Layout (high level)

```
.
├── run.py                 # Desktop entry point
├── LICENSE
├── README.md
├── backend/
│   ├── manage.py
│   ├── run_tests.py       # Verbose test runner with timing
│   ├── requirements.txt
│   ├── .env
│   ├── config/            # settings, urls, api_router, asgi/wsgi
│   ├── common/            # ApiResponse, permissions, models, exceptions
│   └── apps/
│       ├── inventory/     # models, services, views, filters, tests
│       │                  # includes StockStatusService / stock-status API
│       ├── sales/
│       ├── purchases/
│       ├── users/         # models, services, auth_views, filters, admin
│       └── accounting/    # stub — see apps/accounting/README.md
└── frontend/
    ├── main.py
    ├── requirements.txt
    ├── api/
    ├── services/          # inventory (incl. stock-status), sales, purchases
    ├── controllers/       # inventory (incl. StockStatusController), sales, …
    ├── ui/
    │   ├── main_window.py # Sidebar + content stack (no menu bar)
    │   ├── components/    # Sidebar (About + Logout footer), StatusBar, …
    │   ├── views/         # InventoryView, PanelView (closable report tabs), …
    │   ├── tabs/          # Entity tabs + stock status + panel
    │   ├── dialogs/
    │   └── widgets/       # Navbar (generic flag checkbox), tables, …
    └── utils/             # constants (LOW_STOCK_COLOURS, column maps), …
```

---

## Development Notes

- Accounting is present but commented out of `INSTALLED_APPS` until implemented.
- API docs: Scalar at `/api/docs/`, OpenAPI schema at `/api/schema/`.
- Inventory quantity changes run inside `@transaction.atomic` with row-level locking.
- Prefer `select_for_update(of=("self",))` when combining locks with `select_related` on nullable FKs (e.g. invoice `order`).
- Model defaults for dates (`order_date`, `invoice_date`, `payment_date`) must not be overridden with explicit `None` in services.
- Navbar **`flag`** checkbox is generic; tabs call `configure_flag(label, tooltip=...)` (Stock Status uses “Low stock only”).
- Django admin is registered for inventory, sales, and purchases models.

---

## License

MIT — see [LICENSE](LICENSE).

---

# CreatedBy: `CHESyrian` With Help: `Grok Ai`
