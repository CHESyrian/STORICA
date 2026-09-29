"""
BatchController — inventory screen controller for Batches.

Pulls the shared InventoryService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class BatchController:

    def __init__(self):
        # Single line — no api_client argument, no InventoryService wrapper.
        self.inventory = Services.inventory

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        return self.inventory.get_all(model)

    # ------------------------------------------------------------------
    # Batches
    # ------------------------------------------------------------------
    def load_batches(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None, 
        status: str | None = None, 
        warehouse: int | None = None, 
        is_active: bool | None = None,
        ordering: str | None = None, 
        variant: int | None = None, 
    ) -> APIResult:
        """
        Fetch the batch list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.inventory.list_batches(
            page=page,
            page_size=page_size,
            search=search,
            variant=variant,
            warehouse=warehouse,
            is_active=is_active or None,
            ordering=ordering,
            status=status,
        )

        if result.ok:
            logger.debug(
                "Batches loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load batches: %s", result.error)

        return result

    def create_batch(self, batch_data: dict[str, Any]) -> APIResult:
        """Create a new batch."""
        result = self.inventory.create_batch(batch_data)

        if result.ok:
            logger.debug("Batch created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create batch: %s", result.error)

        return result

    def get_batch(self, batch_id: int) -> APIResult:
        """Retrieve a specific batch."""
        result = self.inventory.get_batch(batch_id)

        if result.ok:
            logger.debug("Batch loaded: %s", batch_id)

        else:
            logger.warning("Failed to load batch %s: %s", batch_id, result.error)

        return result

    def update_batch(self, batch_id: int, batch_data: dict[str, Any]) -> APIResult:
        """Fully update a batch."""
        result = self.inventory.update_batch(batch_id, batch_data)

        if result.ok:
            logger.debug("Batch updated: %s", batch_id)

        else:
            logger.warning("Failed to update batch %s: %s", batch_id, result.error)

        return result

    def partial_update_batch(self, batch_id: int, batch_data: dict[str, Any]) -> APIResult:
        """Partially update a batch."""
        result = self.inventory.partial_update_batch(batch_id, batch_data)

        if result.ok:
            logger.debug("Batch partially updated: %s", batch_id)

        else:
            logger.warning("Failed to partially update batch %s: %s", batch_id, result.error)

        return result

    def delete_batch(self, batch_id: int) -> APIResult:
        """Delete a batch."""
        result = self.inventory.delete_batch(batch_id)

        if result.ok:
            logger.debug("Batch deleted: %s", batch_id)

        else:
            logger.warning("Failed to delete batch %s: %s", batch_id, result.error)

        return result