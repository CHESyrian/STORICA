"""
SalesOrderItemController — sales screen controller for Sales Order Items.

Pulls the shared SalesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class SalesOrderItemController:

    def __init__(self):
        # Single line — no api_client argument, no SalesService wrapper.
        self.sales = Services.sales

    # ------------------------------------------------------------------
    # Sales Order Items
    # ------------------------------------------------------------------

    def load_sales_order_items(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        order: int | None = None,
        variant: int | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the sales order item list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.sales.list_sales_order_items(
            page=page,
            page_size=page_size,
            search=search,
            order=order,
            variant=variant,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Sales order items loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load sales order items: %s", result.error)

        return result

    def create_sales_order_item(self, item_data: dict[str, Any]) -> APIResult:
        """Create a new sales order item."""
        result = self.sales.create_sales_order_item(item_data)

        if result.ok:
            logger.debug("Sales order item created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create sales order item: %s", result.error)

        return result

    def get_sales_order_item(self, item_id: int) -> APIResult:
        """Retrieve a specific sales order item."""
        result = self.sales.get_sales_order_item(item_id)

        if result.ok:
            logger.debug("Sales order item loaded: %s", item_id)
        else:
            logger.warning("Failed to load sales order item %s: %s", item_id, result.error)

        return result

    def update_sales_order_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """Fully update a sales order item."""
        result = self.sales.update_sales_order_item(item_id, item_data)

        if result.ok:
            logger.debug("Sales order item updated: %s", item_id)
        else:
            logger.warning("Failed to update sales order item %s: %s", item_id, result.error)

        return result

    def partial_update_sales_order_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """Partially update a sales order item."""
        result = self.sales.partial_update_sales_order_item(item_id, item_data)

        if result.ok:
            logger.debug("Sales order item partially updated: %s", item_id)
        else:
            logger.warning(
                "Failed to partially update sales order item %s: %s", item_id, result.error
            )

        return result

    def delete_sales_order_item(self, item_id: int) -> APIResult:
        """Delete a sales order item."""
        result = self.sales.delete_sales_order_item(item_id)

        if result.ok:
            logger.debug("Sales order item deleted: %s", item_id)
        else:
            logger.warning("Failed to delete sales order item %s: %s", item_id, result.error)

        return result
