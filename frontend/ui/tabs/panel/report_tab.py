"""
Report workspace tab (closable) for the Panel page.

Layout for every report:
  1. KPIs     — metric cards (theme object names only)
  2. Summary  — structured narrative of what the numbers show
  3. Conclusion — short takeaway / recommended next step
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QFrame,
    QGridLayout,
    QSizePolicy,
    QScrollArea,
)

from frontend.api import APIResult, AsyncExecutor
from frontend.controllers import PanelController
from frontend.ui.widgets import LoadingOverlay


class ReportTab(QWidget):
    """
    Closable report tab body.

    ``report_type`` selects which summary to build. Parent opens this
    widget with ``closable=True``.
    """

    REPORT_META: dict[str, dict[str, str]] = {
        "inventory": {
            "title": "Inventory Report",
            "blurb": (
                "On-hand stock by variant and warehouse: quantities, "
                "cost value, and low-stock exposure."
            ),
        },
        "stock_movement": {
            "title": "Stock Movement Report",
            "blurb": (
                "Recent stock movements by type and status "
                "(IN, OUT, TRANSFER, ADJUSTMENT, RETURN)."
            ),
        },
        "sales": {
            "title": "Sales Report",
            "blurb": (
                "Orders, invoices, payments, and ledger income / expense."
            ),
        },
        "product_performance": {
            "title": "Product Performance",
            "blurb": (
                "Products and variants ranked by on-hand quantity "
                "(proxy until dedicated sales analytics exist)."
            ),
        },
        "warehouse_summary": {
            "title": "Warehouse Summary",
            "blurb": (
                "Per-warehouse stock totals and low-stock exposure."
            ),
        },
        "category_analysis": {
            "title": "Category Analysis",
            "blurb": (
                "Category-level product and stock distribution."
            ),
        },
    }

    def __init__(self, report_type: str, title: str | None = None, parent=None):
        super().__init__(parent)
        self.report_type = report_type
        meta = self.REPORT_META.get(report_type, {})
        self.title = title or meta.get(
            "title", report_type.replace("_", " ").title()
        )
        self.blurb = meta.get(
            "blurb",
            "Report workspace. Live charts and export will follow.",
        )

        self.controller = PanelController()
        self.executor = AsyncExecutor()
        self.overlay = LoadingOverlay(self)

        self._stat_labels: dict[str, QLabel] = {}
        self._summary = QTextEdit()
        self._summary.setReadOnly(True)
        self._summary.setObjectName("reportSummaryBody")
        self._summary.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )
        self._summary.setMinimumHeight(80)
        self._conclusion = QTextEdit()
        self._conclusion.setReadOnly(True)
        self._conclusion.setObjectName("reportConclusionBody")
        self._conclusion.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )
        self._conclusion.setMinimumHeight(60)

        self._build_ui()
        self.reload()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        self.setObjectName("reportPage")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("reportScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        outer.addWidget(scroll)

        content = QWidget()
        content.setObjectName("reportContent")
        root = QVBoxLayout(content)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        header = QHBoxLayout()
        heading = QLabel(self.title)
        heading.setObjectName("reportHeading")
        header.addWidget(heading)
        header.addStretch()

        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.setObjectName("reportRefreshBtn")
        self._refresh_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh_btn.clicked.connect(self.reload)
        header.addWidget(self._refresh_btn)
        root.addLayout(header)

        blurb = QLabel(self.blurb)
        blurb.setObjectName("reportBlurb")
        blurb.setWordWrap(True)
        root.addWidget(blurb)

        # --- KPIs (cards) ---
        kpi_label = QLabel("KPIs")
        kpi_label.setObjectName("reportSectionLabel")
        root.addWidget(kpi_label)

        self._cards_host = QWidget()
        self._cards_host.setObjectName("reportCardsHost")
        self._cards_host.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )
        self._cards_layout = QGridLayout(self._cards_host)
        self._cards_layout.setContentsMargins(0, 0, 0, 0)
        self._cards_layout.setSpacing(12)
        root.addWidget(self._cards_host)

        # --- Summary (auto height) ---
        summary_label = QLabel("Summary")
        summary_label.setObjectName("reportSectionLabel")
        root.addWidget(summary_label)
        root.addWidget(self._summary)

        # --- Conclusion (auto height) ---
        conclusion_label = QLabel("Conclusion")
        conclusion_label.setObjectName("reportSectionLabel")
        root.addWidget(conclusion_label)
        root.addWidget(self._conclusion)

        hint = QLabel(
            "This tab is closable — use the × on the tab bar when finished."
        )
        hint.setObjectName("reportHint")
        root.addWidget(hint)
        root.addStretch(1)

        scroll.setWidget(content)

    def _make_card(self, key: str, caption: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("reportStatCard")
        frame.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )
        frame.setMinimumHeight(72)
        lay = QVBoxLayout(frame)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(6)

        cap = QLabel(caption)
        cap.setObjectName("reportStatCaption")
        value = QLabel("—")
        value.setObjectName("reportStatValue")
        value.setWordWrap(True)
        lay.addWidget(cap)
        lay.addWidget(value)
        lay.addStretch(1)
        self._stat_labels[key] = value
        return frame

    def _set_cards(self, specs: list[tuple[str, str]]) -> None:
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._stat_labels.clear()

        cols = min(4, max(1, len(specs)))
        for i, (key, caption) in enumerate(specs):
            card = self._make_card(key, caption)
            self._cards_layout.addWidget(card, i // cols, i % cols)

    def _set_stat(self, key: str, value: Any) -> None:
        label = self._stat_labels.get(key)
        if label is not None:
            label.setText(str(value))

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def reload(self) -> None:
        self.overlay.show_message("Loading report…")
        self.executor.run(
            self._fetch_summary,
            on_result=self._on_loaded,
            on_error=self._on_error,
            on_finished=self._on_finished,
        )

    def refresh(self) -> None:
        self.reload()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.overlay:
            self.overlay.setGeometry(self.rect())

    def _on_loaded(self, data: dict[str, Any]) -> None:
        if not isinstance(data, dict):
            self._summary.setPlainText("Unexpected report payload.")
            self._conclusion.setPlainText("")
            return

        kpis = data.get("kpis") or data.get("cards") or []
        values = data.get("values") or {}
        self._set_cards([(k, c) for k, c in kpis])
        for key, val in values.items():
            self._set_stat(key, val)

        summary = data.get("summary") or data.get("html") or ""
        if summary.strip().startswith("<"):
            self._summary.setHtml(summary)
        else:
            self._summary.setPlainText(summary)

        conclusion = data.get("conclusion") or ""
        if conclusion.strip().startswith("<"):
            self._conclusion.setHtml(conclusion)
        else:
            self._conclusion.setPlainText(conclusion)

    def _on_error(self, err: Any) -> None:
        self._summary.setPlainText(f"Failed to load report:\n{err}")
        self._conclusion.setPlainText(
            "Could not build a conclusion because the report failed to load."
        )

    def _on_finished(self) -> None:
        self.overlay.hide()

    def _fetch_summary(self) -> dict[str, Any]:
        rt = self.report_type
        if rt == "inventory":
            return self._summary_inventory()
        if rt == "stock_movement":
            return self._summary_stock_movement()
        if rt == "sales":
            return self._summary_sales()
        if rt == "product_performance":
            return self._summary_product_performance()
        if rt == "warehouse_summary":
            return self._summary_warehouse()
        if rt == "category_analysis":
            return self._summary_category()
        return {
            "kpis": [("info", "Status")],
            "values": {"info": "N/A"},
            "summary": f"Unknown report type: {rt}",
            "conclusion": "Choose a supported report from the Panel.",
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _page_rows(res: APIResult | None) -> tuple[list, Any]:
        if not res or not res.ok or not isinstance(res.data, dict):
            return [], "?"
        rows = res.data.get("data") or res.data.get("results") or []
        if not isinstance(rows, list):
            rows = []
        pag = res.data.get("paginator") or {}
        return rows, pag.get("count", len(rows))

    @staticmethod
    def _count(res: APIResult) -> str:
        if not res.ok or not isinstance(res.data, dict):
            return "?"
        pag = res.data.get("paginator") or {}
        if "count" in pag:
            return str(pag["count"])
        data = res.data.get("data")
        return str(len(data)) if isinstance(data, list) else "?"

    # ------------------------------------------------------------------
    # Per-report builders
    # ------------------------------------------------------------------

    def _summary_inventory(self) -> dict[str, Any]:
        status = self.controller.inventory.get_all_stock_status()
        products = self.controller.inventory.list_products(page=1, page_size=1)
        variants = self.controller.inventory.list_variants(page=1, page_size=1)
        batches = self.controller.inventory.list_batches(page=1, page_size=1)

        rows: list = []
        if status.ok and isinstance(status.data, dict):
            rows = status.data.get("data") or status.data.get("results") or []
            if not isinstance(rows, list):
                rows = []

        total_qty = Decimal("0")
        total_value = Decimal("0")
        low = 0
        for r in rows:
            if not isinstance(r, dict):
                continue
            total_qty += Decimal(str(r.get("quantity") or 0))
            total_value += Decimal(str(r.get("cost_value") or 0))
            if r.get("is_low_stock"):
                low += 1

        ranked = sorted(
            (r for r in rows if isinstance(r, dict)),
            key=lambda r: Decimal(str(r.get("quantity") or 0)),
            reverse=True,
        )[:8]

        lines = []
        for r in ranked:
            flag = " (low stock)" if r.get("is_low_stock") else ""
            lines.append(
                f"• {r.get('variant_sku') or '—'} — "
                f"{r.get('product_name') or '—'} @ "
                f"{r.get('warehouse_name') or '—'}: "
                f"qty {r.get('quantity') or 0}, "
                f"value {r.get('cost_value') or 0}{flag}"
            )

        summary = (
            f"Catalog: {self._count(products)} products, "
            f"{self._count(variants)} variants, "
            f"{self._count(batches)} batches.\n"
            f"Stock positions: {len(rows)} rows with total quantity "
            f"{total_qty:.2f} and cost value {total_value:.2f}.\n"
            f"Low-stock positions: {low}.\n\n"
            "Largest positions by quantity:\n"
            + ("\n".join(lines) if lines else "• No stock rows available.")
        )

        if low > 0:
            conclusion = (
                f"{low} position(s) are below minimum stock. "
                "Review purchase needs for those SKUs and confirm "
                "reorder quantities with suppliers."
            )
        elif len(rows) == 0:
            conclusion = (
                "No stock positions found. Receive purchase invoices "
                "or complete stock-in movements to populate inventory."
            )
        else:
            conclusion = (
                "Inventory levels look stable with no low-stock flags "
                "on the current snapshot. Continue monitoring movements "
                "after sales posts."
            )

        return {
            "kpis": [
                ("sku_rows", "Stock rows"),
                ("qty", "On-hand qty"),
                ("value", "Cost value"),
                ("low", "Low-stock"),
                ("products", "Products"),
                ("variants", "Variants"),
                ("batches", "Batches"),
            ],
            "values": {
                "sku_rows": len(rows),
                "qty": f"{total_qty:.2f}",
                "value": f"{total_value:.2f}",
                "low": low,
                "products": self._count(products),
                "variants": self._count(variants),
                "batches": self._count(batches),
            },
            "summary": summary,
            "conclusion": conclusion,
        }

    def _summary_stock_movement(self) -> dict[str, Any]:
        res = self.controller.inventory.list_stock_movements(
            page=1, page_size=50
        )
        rows, total = self._page_rows(res)

        by_type: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for r in rows:
            if not isinstance(r, dict):
                continue
            mt = (r.get("movement_type") or "?").upper()
            st = (r.get("status") or "?").lower()
            by_type[mt] = by_type.get(mt, 0) + 1
            by_status[st] = by_status.get(st, 0) + 1

        type_lines = "\n".join(
            f"• {k}: {v}" for k, v in sorted(by_type.items())
        ) or "• None on this page"
        status_lines = "\n".join(
            f"• {k}: {v}" for k, v in sorted(by_status.items())
        ) or "• None on this page"

        recent = [
            r for r in rows[:8] if isinstance(r, dict)
        ]
        recent_lines = "\n".join(
            f"• {r.get('movement_type')} / {r.get('status')} — "
            f"{r.get('product_name') or r.get('product') or '—'} "
            f"qty {r.get('quantity') or 0}"
            f"{(' ref ' + str(r.get('reference_number'))) if r.get('reference_number') else ''}"
            for r in recent
        ) or "• No recent movements"

        pending = by_status.get("pending", 0)
        summary = (
            f"Total movements (all pages): {total}. "
            f"Loaded on this page: {len(rows)}.\n\n"
            f"By type (page):\n{type_lines}\n\n"
            f"By status (page):\n{status_lines}\n\n"
            f"Recent:\n{recent_lines}"
        )

        if pending > 0:
            conclusion = (
                f"{pending} movement(s) are still pending. "
                "Complete or cancel them so stock quantities stay accurate."
            )
        elif len(rows) == 0:
            conclusion = (
                "No movements found. Activity will appear after sales "
                "posts, purchase receipts, or adjustments."
            )
        else:
            conclusion = (
                "Movement flow looks active. Prefer completing pending "
                "items promptly so FIFO allocation and cost posts stay in sync."
            )

        return {
            "kpis": [
                ("total", "Total movements"),
                ("page", "On page"),
                ("pending", "Pending"),
                ("completed", "Completed"),
            ],
            "values": {
                "total": total,
                "page": len(rows),
                "pending": pending,
                "completed": by_status.get("completed", 0),
            },
            "summary": summary,
            "conclusion": conclusion,
        }

    def _summary_sales(self) -> dict[str, Any]:
        orders = self.controller.sales.list_sales_orders(page=1, page_size=50)
        invoices = self.controller.sales.list_sales_invoices(
            page=1, page_size=50
        )
        payments = None
        if hasattr(self.controller.sales, "list_sales_payments"):
            payments = self.controller.sales.list_sales_payments(
                page=1, page_size=50
            )
        customers = self.controller.sales.list_customers(page=1, page_size=1)

        order_rows, order_count = self._page_rows(orders)
        inv_rows, inv_count = self._page_rows(invoices)
        pay_rows, pay_count = self._page_rows(payments)
        _, cust_count = self._page_rows(customers)

        order_status: dict[str, int] = {}
        for r in order_rows:
            if isinstance(r, dict):
                s = (r.get("status") or "?").lower()
                order_status[s] = order_status.get(s, 0) + 1

        inv_total = Decimal("0")
        inv_balance = Decimal("0")
        for r in inv_rows:
            if not isinstance(r, dict):
                continue
            inv_total += Decimal(
                str(r.get("total_amount") or r.get("total") or 0)
            )
            inv_balance += Decimal(
                str(r.get("balance_due") or r.get("balance") or 0)
            )

        status_lines = "\n".join(
            f"• {k}: {v}" for k, v in sorted(order_status.items())
        ) or "• No orders on this page"

        total_income = "—"
        total_expense = "—"
        net_profit = "—"
        pl_extra = ""
        if hasattr(self.controller, "profit_loss"):
            pl_res = self.controller.profit_loss()
            if pl_res.ok and isinstance(pl_res.data, dict):
                payload = pl_res.data.get("data") or pl_res.data
                if isinstance(payload, dict):
                    total_income = payload.get("total_income", "—")
                    total_expense = payload.get("total_expense", "—")
                    net_profit = payload.get("net_profit", "—")
                    pl_extra = (
                        f"\nLedger period "
                        f"{payload.get('date_from')} → {payload.get('date_to')}:"
                        f"\n• Income: {total_income}"
                        f"\n• Expense: {total_expense}"
                        f"\n• Net profit: {net_profit}"
                    )

        draft = order_status.get("draft", 0)
        summary = (
            f"Customers: {cust_count}. Orders: {order_count}. "
            f"Invoices: {inv_count}. Payments: {pay_count}.\n"
            f"Invoice total (page): {inv_total:.2f}. "
            f"Balance due (page): {inv_balance:.2f}.\n\n"
            f"Order status (page):\n{status_lines}"
            f"{pl_extra}"
        )

        if inv_balance > 0:
            conclusion = (
                f"Outstanding balance about {inv_balance:.2f} on loaded invoices. "
                "Follow up on partial / unpaid invoices and record payments."
            )
        elif draft > 0:
            conclusion = (
                f"{draft} draft order(s) on the current page. "
                "Confirm them before creating invoices."
            )
        else:
            conclusion = (
                "Sales pipeline looks clear on this snapshot. "
                "Compare ledger net profit with operational invoice totals "
                "when reconciling the period."
            )

        return {
            "kpis": [
                ("customers", "Customers"),
                ("orders", "Orders"),
                ("invoices", "Invoices"),
                ("payments", "Payments"),
                ("income", "Ledger income"),
                ("expense", "Ledger expense"),
                ("profit", "Net profit"),
                ("inv_total", "Invoice total"),
            ],
            "values": {
                "customers": cust_count,
                "orders": order_count,
                "invoices": inv_count,
                "payments": pay_count,
                "income": total_income,
                "expense": total_expense,
                "profit": net_profit,
                "inv_total": f"{inv_total:.2f}",
            },
            "summary": summary,
            "conclusion": conclusion,
        }

    def _summary_product_performance(self) -> dict[str, Any]:
        status = self.controller.inventory.get_all_stock_status()
        variants = self.controller.inventory.list_variants(page=1, page_size=50)
        products = self.controller.inventory.list_products(page=1, page_size=1)

        rows = []
        if status.ok and isinstance(status.data, dict):
            rows = status.data.get("data") or []
            if not isinstance(rows, list):
                rows = []

        by_product: dict[str, Decimal] = {}
        for r in rows:
            if not isinstance(r, dict):
                continue
            name = r.get("product_name") or str(r.get("product") or "?")
            by_product[name] = by_product.get(name, Decimal("0")) + Decimal(
                str(r.get("quantity") or 0)
            )

        top = sorted(by_product.items(), key=lambda x: x[1], reverse=True)[:10]
        top_lines = "\n".join(
            f"• {n}: {q:.2f}" for n, q in top
        ) or "• No stock data"

        vcount = self._count(variants)
        pcount = self._count(products)

        summary = (
            f"Products: {pcount}. Variants: {vcount}. "
            f"Stock positions: {len(rows)}. "
            f"Products with stock: {len(by_product)}.\n\n"
            f"Top products by on-hand quantity:\n{top_lines}\n\n"
            "Note: ranking uses inventory quantity as a temporary proxy "
            "until dedicated sold-qty analytics are available."
        )

        if not by_product:
            conclusion = (
                "No stocked products to rank. Build inventory via "
                "purchases before performance analysis is meaningful."
            )
        else:
            conclusion = (
                f"Leading product by on-hand stock is "
                f"{top[0][0]} ({top[0][1]:.2f}). "
                "Use sales invoices / movements later for true velocity."
            )

        return {
            "kpis": [
                ("products", "Products"),
                ("variants", "Variants"),
                ("positions", "Stock positions"),
                ("tracked", "With stock"),
            ],
            "values": {
                "products": pcount,
                "variants": vcount,
                "positions": len(rows),
                "tracked": len(by_product),
            },
            "summary": summary,
            "conclusion": conclusion,
        }

    def _summary_warehouse(self) -> dict[str, Any]:
        status = self.controller.inventory.get_all_stock_status()
        warehouses = self.controller.inventory.list_warehouses(
            page=1, page_size=50
        )

        rows = []
        if status.ok and isinstance(status.data, dict):
            rows = status.data.get("data") or []
            if not isinstance(rows, list):
                rows = []

        by_wh: dict[str, dict[str, Any]] = {}
        for r in rows:
            if not isinstance(r, dict):
                continue
            name = r.get("warehouse_name") or str(r.get("warehouse") or "?")
            bucket = by_wh.setdefault(
                name,
                {"qty": Decimal("0"), "value": Decimal("0"), "low": 0},
            )
            bucket["qty"] += Decimal(str(r.get("quantity") or 0))
            bucket["value"] += Decimal(str(r.get("cost_value") or 0))
            if r.get("is_low_stock"):
                bucket["low"] += 1

        lines = "\n".join(
            f"• {name}: qty {d['qty']:.2f}, value {d['value']:.2f}, "
            f"low {d['low']}"
            for name, d in sorted(by_wh.items())
        ) or "• No warehouse stock rows"

        wh_count = self._count(warehouses)
        total_low = sum(d["low"] for d in by_wh.values())

        summary = (
            f"Warehouses: {wh_count}. "
            f"Warehouses with stock rows: {len(by_wh)}.\n\n"
            f"Per warehouse:\n{lines}"
        )

        if total_low > 0:
            conclusion = (
                f"{total_low} low-stock row(s) across warehouses. "
                "Prioritize replenishment for the warehouses with the "
                "highest low counts."
            )
        elif not by_wh:
            conclusion = (
                "No warehouse stock yet. Receive purchases into a "
                "warehouse to start this summary."
            )
        else:
            conclusion = (
                "Stock is distributed with no low-stock flags on this "
                "snapshot. Re-check after large outbound sales."
            )

        return {
            "kpis": [
                ("warehouses", "Warehouses"),
                ("with_stock", "With stock"),
                ("positions", "Positions"),
                ("low", "Low-stock rows"),
            ],
            "values": {
                "warehouses": wh_count,
                "with_stock": len(by_wh),
                "positions": len(rows),
                "low": total_low,
            },
            "summary": summary,
            "conclusion": conclusion,
        }

    def _summary_category(self) -> dict[str, Any]:
        products = self.controller.inventory.list_products(
            page=1, page_size=100
        )
        categories = self.controller.inventory.list_categories(
            page=1, page_size=50
        )

        prod_rows, prod_count = self._page_rows(products)
        cat_rows, cat_count = self._page_rows(categories)

        by_cat: dict[str, int] = {}
        for r in prod_rows:
            if not isinstance(r, dict):
                continue
            name = (
                r.get("category_name")
                or str(r.get("category") or "Uncategorized")
            )
            by_cat[name] = by_cat.get(name, 0) + 1

        lines = "\n".join(
            f"• {name}: {n} product(s)"
            for name, n in sorted(
                by_cat.items(), key=lambda x: x[1], reverse=True
            )
        ) or "• No products on this page"

        summary = (
            f"Categories: {cat_count}. Products (page/count): "
            f"{len(prod_rows)} / {prod_count}.\n\n"
            f"Products per category (page):\n{lines}"
        )

        if not by_cat:
            conclusion = (
                "No categorized products found on this page. "
                "Assign categories when creating products for clearer analysis."
            )
        else:
            top_name, top_n = max(by_cat.items(), key=lambda x: x[1])
            conclusion = (
                f"Largest category on this page is {top_name} "
                f"({top_n} products). Balance catalog coverage if other "
                "categories are intentionally under-represented."
            )

        return {
            "kpis": [
                ("categories", "Categories"),
                ("products", "Products"),
                ("on_page", "Products on page"),
                ("buckets", "Categories used"),
            ],
            "values": {
                "categories": cat_count,
                "products": prod_count,
                "on_page": len(prod_rows),
                "buckets": len(by_cat),
            },
            "summary": summary,
            "conclusion": conclusion,
        }
