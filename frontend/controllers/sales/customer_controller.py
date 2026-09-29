"""
CustomerController — sales screen controller for Customers.

Pulls the shared SalesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class CustomerController:

    def __init__(self):
        # Single line — no api_client argument, no SalesService wrapper.
        self.sales = Services.sales

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------

    def load_customers(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the customer list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.sales.list_customers(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active or None,
            is_verified=is_verified,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Customers loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load customers: %s", result.error)

        return result

    def create_customer(self, customer_data: dict[str, Any]) -> APIResult:
        """Create a new customer."""
        result = self.sales.create_customer(customer_data)

        if result.ok:
            logger.debug("Customer created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create customer: %s", result.error)

        return result

    def get_customer(self, customer_id: int) -> APIResult:
        """Retrieve a specific customer."""
        result = self.sales.get_customer(customer_id)

        if result.ok:
            logger.debug("Customer loaded: %s", customer_id)
        else:
            logger.warning("Failed to load customer %s: %s", customer_id, result.error)

        return result

    def update_customer(self, customer_id: int, customer_data: dict[str, Any]) -> APIResult:
        """Fully update a customer."""
        result = self.sales.update_customer(customer_id, customer_data)

        if result.ok:
            logger.debug("Customer updated: %s", customer_id)
        else:
            logger.warning("Failed to update customer %s: %s", customer_id, result.error)

        return result

    def partial_update_customer(self, customer_id: int, customer_data: dict[str, Any]) -> APIResult:
        """Partially update a customer."""
        result = self.sales.partial_update_customer(customer_id, customer_data)

        if result.ok:
            logger.debug("Customer partially updated: %s", customer_id)
        else:
            logger.warning("Failed to partially update customer %s: %s", customer_id, result.error)

        return result

    def delete_customer(self, customer_id: int) -> APIResult:
        """Delete a customer."""
        result = self.sales.delete_customer(customer_id)

        if result.ok:
            logger.debug("Customer deleted: %s", customer_id)
        else:
            logger.warning("Failed to delete customer %s: %s", customer_id, result.error)

        return result
