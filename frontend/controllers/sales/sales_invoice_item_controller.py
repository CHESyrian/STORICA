"""
SalesInvoiceItemController — sales screen controller for Sales Invoice Items.

Pulls the shared SalesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class SalesInvoiceItemController:

    def __init__(self):
        # Single line — no api_client argument, no SalesService wrapper.
        self.sales = Services.sales

    # ------------------------------------------------------------------
    # Sales Invoice Items
    # ------------------------------------------------------------------

    def load_sales_invoice_items(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        invoice: int | None = None,
        variant: int | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the sales invoice item list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.sales.list_sales_invoice_items(
            page=page,
            page_size=page_size,
            search=search,
            invoice=invoice,
            variant=variant,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Sales invoice items loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load sales invoice items: %s", result.error)

        return result

    def create_sales_invoice_item(self, item_data: dict[str, Any]) -> APIResult:
        """Create a new sales invoice item."""
        result = self.sales.create_sales_invoice_item(item_data)

        if result.ok:
            logger.debug("Sales invoice item created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create sales invoice item: %s", result.error)

        return result

    def get_sales_invoice_item(self, item_id: int) -> APIResult:
        """Retrieve a specific sales invoice item."""
        result = self.sales.get_sales_invoice_item(item_id)

        if result.ok:
            logger.debug("Sales invoice item loaded: %s", item_id)
        else:
            logger.warning("Failed to load sales invoice item %s: %s", item_id, result.error)

        return result

    def update_sales_invoice_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """Fully update a sales invoice item."""
        result = self.sales.update_sales_invoice_item(item_id, item_data)

        if result.ok:
            logger.debug("Sales invoice item updated: %s", item_id)
        else:
            logger.warning("Failed to update sales invoice item %s: %s", item_id, result.error)

        return result

    def partial_update_sales_invoice_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """Partially update a sales invoice item."""
        result = self.sales.partial_update_sales_invoice_item(item_id, item_data)

        if result.ok:
            logger.debug("Sales invoice item partially updated: %s", item_id)
        else:
            logger.warning(
                "Failed to partially update sales invoice item %s: %s", item_id, result.error
            )

        return result

    def delete_sales_invoice_item(self, item_id: int) -> APIResult:
        """Delete a sales invoice item."""
        result = self.sales.delete_sales_invoice_item(item_id)

        if result.ok:
            logger.debug("Sales invoice item deleted: %s", item_id)
        else:
            logger.warning("Failed to delete sales invoice item %s: %s", item_id, result.error)

        return result
