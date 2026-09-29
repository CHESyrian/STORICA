"""
PurchaseOrderController — purchases screen controller for Purchase Orders.

Pulls the shared PurchasesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any, Literal

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class PurchaseOrderController:

    def __init__(self):
        # Single line — no api_client argument, no PurchasesService wrapper.
        self.purchases = Services.purchases

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        return self.purchases.get_all(model)

    # ------------------------------------------------------------------
    # Purchase Orders
    # ------------------------------------------------------------------

    def load_purchase_orders(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal[
            "cancelled", "completed", "confirmed", "delivered",
            "draft", "processing", "returned", "shipped"
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None, 
        supplier: int | None = None,
    ) -> APIResult:
        """
        Fetch the purchase order list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.purchases.list_purchase_orders(
            page=page,
            page_size=page_size,
            search=search,
            supplier=supplier,
            status=status,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Purchase orders loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load purchase orders: %s", result.error)

        return result

    def create_purchase_order(self, order_data: dict[str, Any]) -> APIResult:
        """Create a new purchase order."""
        result = self.purchases.create_purchase_order(order_data)

        if result.ok:
            logger.debug("Purchase order created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create purchase order: %s", result.error)

        return result

    def get_purchase_order(self, order_id: int) -> APIResult:
        """Retrieve a specific purchase order."""
        result = self.purchases.get_purchase_order(order_id)

        if result.ok:
            logger.debug("Purchase order loaded: %s", order_id)

        else:
            logger.warning("Failed to load purchase order %s: %s", order_id, result.error)

        return result

    def update_purchase_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """Fully update a purchase order."""
        result = self.purchases.update_purchase_order(order_id, order_data)

        if result.ok:
            logger.debug("Purchase order updated: %s", order_id)

        else:
            logger.warning("Failed to update purchase order %s: %s", order_id, result.error)

        return result

    def partial_update_purchase_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """Partially update a purchase order."""
        result = self.purchases.partial_update_purchase_order(order_id, order_data)

        if result.ok:
            logger.debug("Purchase order partially updated: %s", order_id)

        else:
            logger.warning("Failed to partially update purchase order %s: %s", order_id, result.error)

        return result

    def delete_purchase_order(self, order_id: int) -> APIResult:
        """Delete a purchase order."""
        result = self.purchases.delete_purchase_order(order_id)

        if result.ok:
            logger.debug("Purchase order deleted: %s", order_id)

        else:
            logger.warning("Failed to delete purchase order %s: %s", order_id, result.error)

        return result

    def cancel_purchase_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Cancel a purchase order."""
        result = self.purchases.cancel_purchase_order(order_id, data)

        if result.ok:
            logger.debug("Purchase order cancelled: %s", order_id)
            
        else:
            logger.warning("Failed to cancel purchase order %s: %s", order_id, result.error)

        return result


