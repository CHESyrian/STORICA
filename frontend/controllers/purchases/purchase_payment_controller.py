"""
PurchasePaymentController — purchases screen controller for Purchase Payments.

Pulls the shared PurchasesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any, Literal

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class PurchasePaymentController:

    def __init__(self):
        # Single line — no api_client argument, no PurchasesService wrapper.
        self.purchases = Services.purchases

    # ------------------------------------------------------------------
    # Purchase Payments
    # ------------------------------------------------------------------

    def load_purchase_payments(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        supplier: int | None = None,
        order: int | None = None,
        invoice: int | None = None,
        status: Literal["completed", "failed", "partial", "pending", "refunded"] | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the purchase payment list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.purchases.list_purchase_payments(
            page=page,
            page_size=page_size,
            search=search,
            supplier=supplier,
            order=order,
            invoice=invoice,
            status=status,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Purchase payments loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load purchase payments: %s", result.error)

        return result

    def create_purchase_payment(self, payment_data: dict[str, Any]) -> APIResult:
        """Create a new purchase payment."""
        result = self.purchases.create_purchase_payment(payment_data)

        if result.ok:
            logger.debug("Purchase payment created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create purchase payment: %s", result.error)

        return result

    def get_purchase_payment(self, payment_id: int) -> APIResult:
        """Retrieve a specific purchase payment."""
        result = self.purchases.get_purchase_payment(payment_id)

        if result.ok:
            logger.debug("Purchase payment loaded: %s", payment_id)
        else:
            logger.warning("Failed to load purchase payment %s: %s", payment_id, result.error)

        return result

    def update_purchase_payment(self, payment_id: int, payment_data: dict[str, Any]) -> APIResult:
        """Fully update a purchase payment."""
        result = self.purchases.update_purchase_payment(payment_id, payment_data)

        if result.ok:
            logger.debug("Purchase payment updated: %s", payment_id)
        else:
            logger.warning("Failed to update purchase payment %s: %s", payment_id, result.error)

        return result

    def partial_update_purchase_payment(self, payment_id: int, payment_data: dict[str, Any]) -> APIResult:
        """Partially update a purchase payment."""
        result = self.purchases.partial_update_purchase_payment(payment_id, payment_data)

        if result.ok:
            logger.debug("Purchase payment partially updated: %s", payment_id)
        else:
            logger.warning(
                "Failed to partially update purchase payment %s: %s", payment_id, result.error
            )

        return result

    def delete_purchase_payment(self, payment_id: int) -> APIResult:
        """Delete a purchase payment."""
        result = self.purchases.delete_purchase_payment(payment_id)

        if result.ok:
            logger.debug("Purchase payment deleted: %s", payment_id)
        else:
            logger.warning("Failed to delete purchase payment %s: %s", payment_id, result.error)

        return result
