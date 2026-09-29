"""
VariantController — inventory screen controller for Variants.

Pulls the shared InventoryService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class VariantController:

    def __init__(self):
        # Single line — no api_client argument, no InventoryService wrapper.
        self.inventory = Services.inventory

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        return self.inventory.get_all(model)

    # ------------------------------------------------------------------
    # Variants
    # ------------------------------------------------------------------

    def load_variants(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        product: int | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the variant list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.inventory.list_variants(
            page=page,
            page_size=page_size,
            search=search,
            product=product,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Variants loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load variants: %s", result.error)

        return result

    def create_variant(self, variant_data: dict[str, Any]) -> APIResult:
        """Create a new variant."""
        result = self.inventory.create_variant(variant_data)

        if result.ok:
            logger.debug("Variant created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create variant: %s", result.error)

        return result

    def get_variant(self, variant_id: int) -> APIResult:
        """Retrieve a specific variant."""
        result = self.inventory.get_variant(variant_id)

        if result.ok:
            logger.debug("Variant loaded: %s", variant_id)
        else:
            logger.warning("Failed to load variant %s: %s", variant_id, result.error)

        return result

    def update_variant(self, variant_id: int, variant_data: dict[str, Any]) -> APIResult:
        """Fully update a variant."""
        result = self.inventory.update_variant(variant_id, variant_data)

        if result.ok:
            logger.debug("Variant updated: %s", variant_id)
        else:
            logger.warning("Failed to update variant %s: %s", variant_id, result.error)

        return result

    def partial_update_variant(self, variant_id: int, variant_data: dict[str, Any]) -> APIResult:
        """Partially update a variant."""
        result = self.inventory.partial_update_variant(variant_id, variant_data)

        if result.ok:
            logger.debug("Variant partially updated: %s", variant_id)
        else:
            logger.warning("Failed to partially update variant %s: %s", variant_id, result.error)

        return result

    def delete_variant(self, variant_id: int) -> APIResult:
        """Delete a variant."""
        result = self.inventory.delete_variant(variant_id)

        if result.ok:
            logger.debug("Variant deleted: %s", variant_id)
        else:
            logger.warning("Failed to delete variant %s: %s", variant_id, result.error)

        return result
