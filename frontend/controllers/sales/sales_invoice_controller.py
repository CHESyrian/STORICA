"""
SalesInvoiceController — sales screen controller for Sales Invoices.

Pulls the shared SalesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any, Literal

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class SalesInvoiceController:

    def __init__(self):
        # Single line — no api_client argument, no SalesService wrapper.
        self.sales = Services.sales

    # ------------------------------------------------------------------
    # Sales Invoices
    # ------------------------------------------------------------------

    def load_sales_invoices(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        customer: int | None = None,
        order: int | None = None,
        status: Literal[
            "cancelled", "draft", "overdue", "paid", "partial", "refunded", "sent"
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the sales invoice list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.sales.list_sales_invoices(
            page=page,
            page_size=page_size,
            search=search,
            customer=customer,
            order=order,
            status=status,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Sales invoices loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load sales invoices: %s", result.error)

        return result

    def create_sales_invoice(self, invoice_data: dict[str, Any]) -> APIResult:
        """Create a new sales invoice."""
        result = self.sales.create_sales_invoice(invoice_data)

        if result.ok:
            logger.debug("Sales invoice created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create sales invoice: %s", result.error)

        return result

    def get_sales_invoice(self, invoice_id: int) -> APIResult:
        """Retrieve a specific sales invoice."""
        result = self.sales.get_sales_invoice(invoice_id)

        if result.ok:
            logger.debug("Sales invoice loaded: %s", invoice_id)
        else:
            logger.warning("Failed to load sales invoice %s: %s", invoice_id, result.error)

        return result

    def update_sales_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """Fully update a sales invoice."""
        result = self.sales.update_sales_invoice(invoice_id, invoice_data)

        if result.ok:
            logger.debug("Sales invoice updated: %s", invoice_id)
        else:
            logger.warning("Failed to update sales invoice %s: %s", invoice_id, result.error)

        return result

    def partial_update_sales_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """Partially update a sales invoice."""
        result = self.sales.partial_update_sales_invoice(invoice_id, invoice_data)

        if result.ok:
            logger.debug("Sales invoice partially updated: %s", invoice_id)
        else:
            logger.warning(
                "Failed to partially update sales invoice %s: %s", invoice_id, result.error
            )

        return result

    def delete_sales_invoice(self, invoice_id: int) -> APIResult:
        """Delete a sales invoice."""
        result = self.sales.delete_sales_invoice(invoice_id)

        if result.ok:
            logger.debug("Sales invoice deleted: %s", invoice_id)
        else:
            logger.warning("Failed to delete sales invoice %s: %s", invoice_id, result.error)

        return result

    def post_sales_invoice(self, invoice_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Post a sales invoice."""
        result = self.sales.post_sales_invoice(invoice_id, data)

        if result.ok:
            logger.debug("Sales invoice posted: %s", invoice_id)
        else:
            logger.warning("Failed to post sales invoice %s: %s", invoice_id, result.error)

        return result
