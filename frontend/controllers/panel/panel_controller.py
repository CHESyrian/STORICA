"""
PanelController — controller for quick-create panel/dialog actions.

Thin pass-through controller mirroring ExampleController's pattern.
Pulls InventoryService, PurchasesService, and SalesService from the
Services singleton. No auth_client or service instantiation here.
"""

from __future__ import annotations

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class PanelController:

    def __init__(self) -> None:
        self.inventory = Services.inventory
        self.purchases = Services.purchases
        self.sales     = Services.sales
        self.general   = Services.general


    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        return self.general.get_all(model)

    def trial_balance(self, as_of: str | None = None) -> APIResult:
        return self.general.trial_balance(as_of=as_of)

    def profit_loss(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> APIResult:
        return self.general.profit_loss(
            date_from=date_from, date_to=date_to
        )

    # ------------------------------------------------------------------
    # Warehouse
    # ------------------------------------------------------------------

    def create_warehouse(self, warehouse_data: dict[str, Any]) -> APIResult:
        """Create a new warehouse and return the raw APIResult."""
        result = self.inventory.create_warehouse(warehouse_data)

        if result.ok:
            logger.debug("Warehouse created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create warehouse: %s", result.error)

        return result

    # ------------------------------------------------------------------
    # Category
    # ------------------------------------------------------------------

    def create_category(self, category_data: dict[str, Any]) -> APIResult:
        """Create a new category and return the raw APIResult."""
        result = self.inventory.create_category(category_data)

        if result.ok:
            logger.debug("Category created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create category: %s", result.error)

        return result


    # ------------------------------------------------------------------
    # Product
    # ------------------------------------------------------------------

    def create_product(self, product_data: dict[str, Any]) -> APIResult:
        """Create a new product and return the raw APIResult."""
        result = self.inventory.create_product(product_data)

        if result.ok:
            logger.debug("Product created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create product: %s", result.error)

        return result

    # ------------------------------------------------------------------
    # Variant
    # ------------------------------------------------------------------

    def create_variant(self, variant_data: dict[str, Any]) -> APIResult:
        """Create a new variant and return the raw APIResult."""
        result = self.inventory.create_variant(variant_data)

        if result.ok:
            logger.debug("Variant created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create variant: %s", result.error)

        return result

    # ------------------------------------------------------------------
    # Supplier
    # ------------------------------------------------------------------

    def create_supplier(self, supplier_data: dict[str, Any]) -> APIResult:
        """Create a new supplier and return the raw APIResult."""
        result = self.purchases.create_supplier(supplier_data)

        if result.ok:
            logger.debug("Supplier created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create supplier: %s", result.error)

        return result

    # ------------------------------------------------------------------
    # Customer
    # ------------------------------------------------------------------

    def create_customer(self, customer_data: dict[str, Any]) -> APIResult:
        """Create a new customer and return the raw APIResult."""
        result = self.sales.create_customer(customer_data)

        if result.ok:
            logger.debug("Customer created: %s", result.data.get("id"))
            
        else:
            logger.warning("Failed to create customer: %s", result.error)

        return result
