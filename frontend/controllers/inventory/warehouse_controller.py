"""
WarehouseController — inventory screen controller for Warehouses.

Pulls the shared InventoryService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any, Literal

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class WarehouseController:

    def __init__(self):
        # Single line — no api_client argument, no InventoryService wrapper.
        self.inventory = Services.inventory

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        return self.inventory.get_all(model)

    # ------------------------------------------------------------------
    # Warehouses
    # ------------------------------------------------------------------

    def load_warehouses(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal["active", "inactive", "maintenance"] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the warehouse list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.inventory.list_warehouses(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active or None,
            status=status,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Warehouses loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load warehouses: %s", result.error)

        return result

    def create_warehouse(self, warehouse_data: dict[str, Any]) -> APIResult:
        """Create a new warehouse."""
        result = self.inventory.create_warehouse(warehouse_data)

        if result.ok:
            logger.debug("Warehouse created: %s", result.data.get("id"))
        else:
            logger.warning("Failed to create warehouse: %s", result.error)

        return result

    def get_warehouse(self, warehouse_id: int) -> APIResult:
        """Retrieve a specific warehouse."""
        result = self.inventory.get_warehouse(warehouse_id)

        if result.ok:
            logger.debug("Warehouse loaded: %s", warehouse_id)
        else:
            logger.warning("Failed to load warehouse %s: %s", warehouse_id, result.error)

        return result

    def update_warehouse(self, warehouse_id: int, warehouse_data: dict[str, Any]) -> APIResult:
        """Fully update a warehouse."""
        result = self.inventory.update_warehouse(warehouse_id, warehouse_data)

        if result.ok:
            logger.debug("Warehouse updated: %s", warehouse_id)
        else:
            logger.warning("Failed to update warehouse %s: %s", warehouse_id, result.error)

        return result

    def partial_update_warehouse(self, warehouse_id: int, warehouse_data: dict[str, Any]) -> APIResult:
        """Partially update a warehouse."""
        result = self.inventory.partial_update_warehouse(warehouse_id, warehouse_data)

        if result.ok:
            logger.debug("Warehouse partially updated: %s", warehouse_id)
        else:
            logger.warning("Failed to partially update warehouse %s: %s", warehouse_id, result.error)

        return result

    def delete_warehouse(self, warehouse_id: int) -> APIResult:
        """Delete a warehouse."""
        result = self.inventory.delete_warehouse(warehouse_id)

        if result.ok:
            logger.debug("Warehouse deleted: %s", warehouse_id)
        else:
            logger.warning("Failed to delete warehouse %s: %s", warehouse_id, result.error)

        return result
