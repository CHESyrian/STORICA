"""
SupplierController — purchases screen controller for Suppliers.

Pulls the shared PurchasesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class SupplierController:

    def __init__(self):
        # Single line — no api_client argument, no PurchasesService wrapper.
        self.purchases = Services.purchases

    # ------------------------------------------------------------------
    # Suppliers
    # ------------------------------------------------------------------

    def load_suppliers(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the supplier list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.purchases.list_suppliers(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active or None,
            is_verified=is_verified,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Suppliers loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load suppliers: %s", result.error)

        return result

    def create_supplier(self, supplier_data: dict[str, Any]) -> APIResult:
        """Create a new supplier."""
        result = self.purchases.create_supplier(supplier_data)

        if result.ok:
            logger.debug("Supplier created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create supplier: %s", result.error)

        return result

    def get_supplier(self, supplier_id: int) -> APIResult:
        """Retrieve a specific supplier."""
        result = self.purchases.get_supplier(supplier_id)

        if result.ok:
            logger.debug("Supplier loaded: %s", supplier_id)
        else:
            logger.warning("Failed to load supplier %s: %s", supplier_id, result.error)

        return result

    def update_supplier(self, supplier_id: int, supplier_data: dict[str, Any]) -> APIResult:
        """Fully update a supplier."""
        result = self.purchases.update_supplier(supplier_id, supplier_data)

        if result.ok:
            logger.debug("Supplier updated: %s", supplier_id)
        else:
            logger.warning("Failed to update supplier %s: %s", supplier_id, result.error)

        return result

    def partial_update_supplier(self, supplier_id: int, supplier_data: dict[str, Any]) -> APIResult:
        """Partially update a supplier."""
        result = self.purchases.partial_update_supplier(supplier_id, supplier_data)

        if result.ok:
            logger.debug("Supplier partially updated: %s", supplier_id)
        else:
            logger.warning("Failed to partially update supplier %s: %s", supplier_id, result.error)

        return result

    def delete_supplier(self, supplier_id: int) -> APIResult:
        """Delete a supplier."""
        result = self.purchases.delete_supplier(supplier_id)

        if result.ok:
            logger.debug("Supplier deleted: %s", supplier_id)
        else:
            logger.warning("Failed to delete supplier %s: %s", supplier_id, result.error)

        return result
