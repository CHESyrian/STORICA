"""
StockMovementController — inventory screen controller for Stock Movements.

Pulls the shared InventoryService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class StockMovementController:

    def __init__(self):
        # Single line — no api_client argument, no InventoryService wrapper.
        self.inventory = Services.inventory

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        return self.inventory.get_all(model)

    # ------------------------------------------------------------------
    # Stock Movements
    # ------------------------------------------------------------------

    def load_stock_movements(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None, 
        movement_type: str | None = None,
        status: str | None = None,
        product: int | None = None,
        batch: int | None = None,
        performed_by: int | None = None,
        from_warehouse: int | None = None,
        to_warehouse: int | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the stock movement list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.inventory.list_stock_movements(
            page=page,
            page_size=page_size,
            search=search,
            movement_type=movement_type,
            status=status,
            product=product,
            batch=batch,
            performed_by=performed_by,
            from_warehouse=from_warehouse,
            to_warehouse=to_warehouse,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Stock movements loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load stock movements: %s", result.error)

        return result

    def create_stock_movement(self, movement_data: dict[str, Any]) -> APIResult:
        """Create a new stock movement."""
        result = self.inventory.create_stock_movement(movement_data)

        if result.ok:
            logger.debug("Stock movement created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create stock movement: %s", result.error)

        return result

    def get_stock_movement(self, movement_id: int) -> APIResult:
        """Retrieve a specific stock movement."""
        result = self.inventory.get_stock_movement(movement_id)

        if result.ok:
            logger.debug("Stock movement loaded: %s", movement_id)
        else:
            logger.warning("Failed to load stock movement %s: %s", movement_id, result.error)

        return result

    def update_stock_movement(self, movement_id: int, movement_data: dict[str, Any]) -> APIResult:
        """Fully update a stock movement."""
        result = self.inventory.update_stock_movement(movement_id, movement_data)

        if result.ok:
            logger.debug("Stock movement updated: %s", movement_id)
        else:
            logger.warning("Failed to update stock movement %s: %s", movement_id, result.error)

        return result

    def partial_update_stock_movement(self, movement_id: int, movement_data: dict[str, Any]) -> APIResult:
        """Partially update a stock movement."""
        result = self.inventory.partial_update_stock_movement(movement_id, movement_data)

        if result.ok:
            logger.debug("Stock movement partially updated: %s", movement_id)
        else:
            logger.warning(
                "Failed to partially update stock movement %s: %s", movement_id, result.error
            )

        return result

    def delete_stock_movement(self, movement_id: int) -> APIResult:
        """Delete a stock movement."""
        result = self.inventory.delete_stock_movement(movement_id)

        if result.ok:
            logger.debug("Stock movement deleted: %s", movement_id)
        else:
            logger.warning("Failed to delete stock movement %s: %s", movement_id, result.error)

        return result
