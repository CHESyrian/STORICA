"""
SalesOrderController — sales screen controller for Sales Orders.

Pulls the shared SalesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any, Literal

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class SalesOrderController:

    def __init__(self):
        # Single line — no api_client argument, no SalesService wrapper.
        self.sales = Services.sales

    # ------------------------------------------------------------------
    # Sales Orders
    # ------------------------------------------------------------------

    def load_sales_orders(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        customer: int | None = None,
        status: Literal[
            "cancelled", "completed", "confirmed", "delivered",
            "draft", "processing", "returned", "shipped"
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the sales order list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.sales.list_sales_orders(
            page=page,
            page_size=page_size,
            search=search,
            customer=customer,
            status=status,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Sales orders loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load sales orders: %s", result.error)

        return result

    def create_sales_order(self, order_data: dict[str, Any]) -> APIResult:
        """Create a new sales order."""
        result = self.sales.create_sales_order(order_data)

        if result.ok:
            logger.debug("Sales order created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create sales order: %s", result.error)

        return result

    def get_sales_order(self, order_id: int) -> APIResult:
        """Retrieve a specific sales order."""
        result = self.sales.get_sales_order(order_id)

        if result.ok:
            logger.debug("Sales order loaded: %s", order_id)
        else:
            logger.warning("Failed to load sales order %s: %s", order_id, result.error)

        return result

    def update_sales_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """Fully update a sales order."""
        result = self.sales.update_sales_order(order_id, order_data)

        if result.ok:
            logger.debug("Sales order updated: %s", order_id)
        else:
            logger.warning("Failed to update sales order %s: %s", order_id, result.error)

        return result

    def partial_update_sales_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """Partially update a sales order."""
        result = self.sales.partial_update_sales_order(order_id, order_data)

        if result.ok:
            logger.debug("Sales order partially updated: %s", order_id)
        else:
            logger.warning("Failed to partially update sales order %s: %s", order_id, result.error)

        return result

    def delete_sales_order(self, order_id: int) -> APIResult:
        """Delete a sales order."""
        result = self.sales.delete_sales_order(order_id)

        if result.ok:
            logger.debug("Sales order deleted: %s", order_id)
        else:
            logger.warning("Failed to delete sales order %s: %s", order_id, result.error)

        return result

    def cancel_sales_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Cancel a sales order."""
        result = self.sales.cancel_sales_order(order_id, data)

        if result.ok:
            logger.debug("Sales order cancelled: %s", order_id)
        else:
            logger.warning("Failed to cancel sales order %s: %s", order_id, result.error)

        return result
