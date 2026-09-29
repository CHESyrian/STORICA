"""
ProductController — inventory screen controller for Products.

Pulls the shared InventoryService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class ProductController:

    def __init__(self):
        # Single line — no api_client argument, no InventoryService wrapper.
        self.inventory = Services.inventory

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        return self.inventory.get_all(model)

    # ------------------------------------------------------------------
    # Products
    # ------------------------------------------------------------------
    def load_products(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        category: str | None = None,
        unit: str | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the product list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.inventory.list_products(
            page=page,
            page_size=page_size,
            search=search,
            category=category,
            unit=unit,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Products loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )

        else:
            logger.warning("Failed to load products: %s", result.error)

        return result

    def create_product(self, product_data: dict[str, Any]) -> APIResult:
        """Create a new product."""
        result = self.inventory.create_product(product_data)

        if result.ok:
            logger.debug("Product created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create product: %s", result.error)

        return result

    def get_product(self, product_id: int) -> APIResult:
        """Retrieve a specific product."""
        result = self.inventory.get_product(product_id)

        if result.ok:
            logger.debug("Product loaded: %s", product_id)

        else:
            logger.warning("Failed to load product %s: %s", product_id, result.error)

        return result

    def update_product(self, product_id: int, product_data: dict[str, Any]) -> APIResult:
        """Fully update a product."""
        result = self.inventory.update_product(product_id, product_data)

        if result.ok:
            logger.debug("Product updated: %s", product_id)

        else:
            logger.warning("Failed to update product %s: %s", product_id, result.error)

        return result

    def partial_update_product(self, product_id: int, product_data: dict[str, Any]) -> APIResult:
        """Partially update a product."""
        result = self.inventory.partial_update_product(product_id, product_data)

        if result.ok:
            logger.debug("Product partially updated: %s", product_id)

        else:
            logger.warning("Failed to partially update product %s: %s", product_id, result.error)

        return result

    def delete_product(self, product_id: int) -> APIResult:
        """Delete a product."""
        result = self.inventory.delete_product(product_id)

        if result.ok:
            logger.debug("Product deleted: %s", product_id)

        else:
            logger.warning("Failed to delete product %s: %s", product_id, result.error)

        return result
