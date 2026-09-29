"""
SalesPaymentController — sales screen controller for Sales Payments.

Pulls the shared SalesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any, Literal

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class SalesPaymentController:

    def __init__(self):
        # Single line — no api_client argument, no SalesService wrapper.
        self.sales = Services.sales

    # ------------------------------------------------------------------
    # Sales Payments
    # ------------------------------------------------------------------

    def load_sales_payments(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        customer: int | None = None,
        order: int | None = None,
        invoice: int | None = None,
        status: Literal["completed", "failed", "partial", "pending", "refunded"] | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the sales payment list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.sales.list_sales_payments(
            page=page,
            page_size=page_size,
            search=search,
            customer=customer,
            order=order,
            invoice=invoice,
            status=status,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Sales payments loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load sales payments: %s", result.error)

        return result

    def create_sales_payment(self, payment_data: dict[str, Any]) -> APIResult:
        """Create a new sales payment."""
        result = self.sales.create_sales_payment(payment_data)

        if result.ok:
            logger.debug("Sales payment created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create sales payment: %s", result.error)

        return result

    def get_sales_payment(self, payment_id: int) -> APIResult:
        """Retrieve a specific sales payment."""
        result = self.sales.get_sales_payment(payment_id)

        if result.ok:
            logger.debug("Sales payment loaded: %s", payment_id)
        else:
            logger.warning("Failed to load sales payment %s: %s", payment_id, result.error)

        return result

    def update_sales_payment(self, payment_id: int, payment_data: dict[str, Any]) -> APIResult:
        """Fully update a sales payment."""
        result = self.sales.update_sales_payment(payment_id, payment_data)

        if result.ok:
            logger.debug("Sales payment updated: %s", payment_id)
        else:
            logger.warning("Failed to update sales payment %s: %s", payment_id, result.error)

        return result

    def partial_update_sales_payment(self, payment_id: int, payment_data: dict[str, Any]) -> APIResult:
        """Partially update a sales payment."""
        result = self.sales.partial_update_sales_payment(payment_id, payment_data)

        if result.ok:
            logger.debug("Sales payment partially updated: %s", payment_id)
        else:
            logger.warning(
                "Failed to partially update sales payment %s: %s", payment_id, result.error
            )

        return result

    def delete_sales_payment(self, payment_id: int) -> APIResult:
        """Delete a sales payment."""
        result = self.sales.delete_sales_payment(payment_id)

        if result.ok:
            logger.debug("Sales payment deleted: %s", payment_id)
        else:
            logger.warning("Failed to delete sales payment %s: %s", payment_id, result.error)

        return result
