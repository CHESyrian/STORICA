"""
PurchaseInvoiceItemController — purchases screen controller for Purchase Invoice Items.

Pulls the shared PurchasesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class PurchaseInvoiceItemController:

    def __init__(self):
        # Single line — no api_client argument, no PurchasesService wrapper.
        self.purchases = Services.purchases

    # ------------------------------------------------------------------
    # Purchase Invoice Items
    # ------------------------------------------------------------------

    def load_purchase_invoice_items(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        invoice: int | None = None,
        variant: int | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the purchase invoice item list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.purchases.list_purchase_invoice_items(
            page=page,
            page_size=page_size,
            search=search,
            invoice=invoice,
            variant=variant,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Purchase invoice items loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load purchase invoice items: %s", result.error)

        return result

    def create_purchase_invoice_item(self, item_data: dict[str, Any]) -> APIResult:
        """Create a new purchase invoice item."""
        result = self.purchases.create_purchase_invoice_item(item_data)

        if result.ok:
            logger.debug("Purchase invoice item created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create purchase invoice item: %s", result.error)

        return result

    def get_purchase_invoice_item(self, item_id: int) -> APIResult:
        """Retrieve a specific purchase invoice item."""
        result = self.purchases.get_purchase_invoice_item(item_id)

        if result.ok:
            logger.debug("Purchase invoice item loaded: %s", item_id)
        else:
            logger.warning("Failed to load purchase invoice item %s: %s", item_id, result.error)

        return result

    def update_purchase_invoice_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """Fully update a purchase invoice item."""
        result = self.purchases.update_purchase_invoice_item(item_id, item_data)

        if result.ok:
            logger.debug("Purchase invoice item updated: %s", item_id)
        else:
            logger.warning("Failed to update purchase invoice item %s: %s", item_id, result.error)

        return result

    def partial_update_purchase_invoice_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """Partially update a purchase invoice item."""
        result = self.purchases.partial_update_purchase_invoice_item(item_id, item_data)

        if result.ok:
            logger.debug("Purchase invoice item partially updated: %s", item_id)
        else:
            logger.warning(
                "Failed to partially update purchase invoice item %s: %s", item_id, result.error
            )

        return result

    def delete_purchase_invoice_item(self, item_id: int) -> APIResult:
        """Delete a purchase invoice item."""
        result = self.purchases.delete_purchase_invoice_item(item_id)

        if result.ok:
            logger.debug("Purchase invoice item deleted: %s", item_id)
        else:
            logger.warning("Failed to delete purchase invoice item %s: %s", item_id, result.error)

        return result
