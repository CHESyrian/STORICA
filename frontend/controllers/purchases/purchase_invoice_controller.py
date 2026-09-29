"""
PurchaseInvoiceController — purchases screen controller for Purchase Invoices.

Pulls the shared PurchasesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any, Literal

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class PurchaseInvoiceController:

    def __init__(self):
        # Single line — no api_client argument, no PurchasesService wrapper.
        self.purchases = Services.purchases

    # ------------------------------------------------------------------
    # Purchase Invoices
    # ------------------------------------------------------------------

    def load_purchase_invoices(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        supplier: int | None = None,
        order: int | None = None,
        status: Literal[
            "cancelled", "draft", "overdue", "paid", "partial", "refunded", "sent"
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the purchase invoice list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.purchases.list_purchase_invoices(
            page=page,
            page_size=page_size,
            search=search,
            supplier=supplier,
            order=order,
            status=status,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Purchase invoices loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load purchase invoices: %s", result.error)

        return result

    def create_purchase_invoice(self, invoice_data: dict[str, Any]) -> APIResult:
        """Create a new purchase invoice."""
        result = self.purchases.create_purchase_invoice(invoice_data)

        if result.ok:
            logger.debug("Purchase invoice created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create purchase invoice: %s", result.error)

        return result

    def get_purchase_invoice(self, invoice_id: int) -> APIResult:
        """Retrieve a specific purchase invoice."""
        result = self.purchases.get_purchase_invoice(invoice_id)

        if result.ok:
            logger.debug("Purchase invoice loaded: %s", invoice_id)

        else:
            logger.warning("Failed to load purchase invoice %s: %s", invoice_id, result.error)

        return result

    def update_purchase_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """Fully update a purchase invoice."""
        result = self.purchases.update_purchase_invoice(invoice_id, invoice_data)

        if result.ok:
            logger.debug("Purchase invoice updated: %s", invoice_id)

        else:
            logger.warning("Failed to update purchase invoice %s: %s", invoice_id, result.error)

        return result

    def partial_update_purchase_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """Partially update a purchase invoice."""
        result = self.purchases.partial_update_purchase_invoice(invoice_id, invoice_data)

        if result.ok:
            logger.debug("Purchase invoice partially updated: %s", invoice_id)

        else:
            logger.warning(
                "Failed to partially update purchase invoice %s: %s", invoice_id, result.error
            )

        return result

    def delete_purchase_invoice(self, invoice_id: int) -> APIResult:
        """Delete a purchase invoice."""
        result = self.purchases.delete_purchase_invoice(invoice_id)

        if result.ok:
            logger.debug("Purchase invoice deleted: %s", invoice_id)

        else:
            logger.warning("Failed to delete purchase invoice %s: %s", invoice_id, result.error)

        return result

    def post_purchase_invoice(self, invoice_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Post a purchase invoice."""
        result = self.purchases.post_purchase_invoice(invoice_id, data)

        if result.ok:
            logger.debug("Purchase invoice posted: %s", invoice_id)
            
        else:
            logger.warning("Failed to post purchase invoice %s: %s", invoice_id, result.error)

        return result
