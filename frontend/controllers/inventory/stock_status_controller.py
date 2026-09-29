"""
StockStatusController — read-only stock levels (variant × warehouse).
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class StockStatusController:

    def __init__(self):
        self.inventory = Services.inventory

    def get_all(self, model: str):
        return self.inventory.get_all(model)

    def load_stock_status(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Any = None,
        choice: Any = None,
        is_active: bool | None = None,
        low_stock: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        ``status`` → warehouse id; ``choice`` → category id when numeric;
        ``low_stock`` True → only rows at/below min_stock.
        """
        warehouse = None
        if status not in (None, ""):
            try:
                warehouse = int(status)
            except (TypeError, ValueError):
                warehouse = None

        category = None
        if choice not in (None, ""):
            try:
                category = int(choice)
            except (TypeError, ValueError):
                category = None

        active = is_active
        if isinstance(is_active, str):
            if is_active.lower() in ("true", "1", "yes"):
                active = True
            elif is_active.lower() in ("false", "0", "no"):
                active = False
            else:
                active = None

        low = low_stock
        if isinstance(low_stock, str):
            low = low_stock.lower() in ("true", "1", "yes")

        low_param = True if low else None

        result = self.inventory.list_stock_status(
            page=page,
            page_size=page_size,
            search=search,
            warehouse=warehouse,
            category=category,
            is_active=active,
            low_stock=low_param,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Stock status loaded: %s rows",
                len(
                    result.data.get("data", [])
                    or result.data.get("results", [])
                ),
            )
        else:
            logger.warning("Failed to load stock status: %s", result.error)

        return result
