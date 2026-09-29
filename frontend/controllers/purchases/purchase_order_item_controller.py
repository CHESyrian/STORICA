"""
PurchaseOrderItemController — purchases screen controller for Purchase Order Items.

Pulls the shared PurchasesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class PurchaseOrderItemController:

    def __init__(self):
        # Single line — no api_client argument, no PurchasesService wrapper.
        self.purchases = Services.purchases

    # ------------------------------------------------------------------
    # Purchase Order Items
    # ------------------------------------------------------------------

    def load_purchase_order_items(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        order: int | None = None,
        variant: int | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the purchase order item list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.purchases.list_purchase_order_items(
            page=page,
            page_size=page_size,
            search=search,
            order=order,
            variant=variant,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Purchase order items loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load purchase order items: %s", result.error)

        return result

    def create_purchase_order_item(self, item_data: dict[str, Any]) -> APIResult:
        """Create a new purchase order item."""
        result = self.purchases.create_purchase_order_item(item_data)

        if result.ok:
            logger.debug("Purchase order item created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create purchase order item: %s", result.error)

        return result

    def get_purchase_order_item(self, item_id: int) -> APIResult:
        """Retrieve a specific purchase order item."""
        result = self.purchases.get_purchase_order_item(item_id)

        if result.ok:
            logger.debug("Purchase order item loaded: %s", item_id)
        else:
            logger.warning("Failed to load purchase order item %s: %s", item_id, result.error)

        return result

    def update_purchase_order_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """Fully update a purchase order item."""
        result = self.purchases.update_purchase_order_item(item_id, item_data)

        if result.ok:
            logger.debug("Purchase order item updated: %s", item_id)
        else:
            logger.warning("Failed to update purchase order item %s: %s", item_id, result.error)

        return result

    def partial_update_purchase_order_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """Partially update a purchase order item."""
        result = self.purchases.partial_update_purchase_order_item(item_id, item_data)

        if result.ok:
            logger.debug("Purchase order item partially updated: %s", item_id)
        else:
            logger.warning(
                "Failed to partially update purchase order item %s: %s", item_id, result.error
            )

        return result

    def delete_purchase_order_item(self, item_id: int) -> APIResult:
        """Delete a purchase order item."""
        result = self.purchases.delete_purchase_order_item(item_id)

        if result.ok:
            logger.debug("Purchase order item deleted: %s", item_id)
        else:
            logger.warning("Failed to delete purchase order item %s: %s", item_id, result.error)

        return result
