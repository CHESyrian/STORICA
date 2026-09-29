"""
CategoryController — inventory screen controller for Categories.

Pulls the shared InventoryService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class CategoryController:

    def __init__(self):
        # Single line — no api_client argument, no InventoryService wrapper.
        self.inventory = Services.inventory

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        return self.inventory.get_all(model)

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def load_categories(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        parent: int | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the category list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.inventory.list_categories(
            page=page,
            page_size=page_size,
            search=search,
            parent=parent,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Categories loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load categories: %s", result.error)

        return result

    def create_category(self, category_data: dict[str, Any]) -> APIResult:
        """Create a new category."""
        result = self.inventory.create_category(category_data)

        if result.ok:
            logger.debug("Category created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create category: %s", result.error)

        return result

    def get_category(self, category_id: int) -> APIResult:
        """Retrieve a specific category."""
        result = self.inventory.get_category(category_id)

        if result.ok:
            logger.debug("Category loaded: %s", category_id)

        else:
            logger.warning("Failed to load category %s: %s", category_id, result.error)

        return result

    def update_category(self, category_id: int, category_data: dict[str, Any]) -> APIResult:
        """Fully update a category."""
        result = self.inventory.update_category(category_id, category_data)

        if result.ok:
            logger.debug("Category updated: %s", category_id)

        else:
            logger.warning("Failed to update category %s: %s", category_id, result.error)

        return result

    def partial_update_category(self, category_id: int, category_data: dict[str, Any]) -> APIResult:
        """Partially update a category."""
        result = self.inventory.partial_update_category(category_id, category_data)

        if result.ok:
            logger.debug("Category partially updated: %s", category_id)

        else:
            logger.warning("Failed to partially update category %s: %s", category_id, result.error)

        return result

    def delete_category(self, category_id: int) -> APIResult:
        """Delete a category."""
        result = self.inventory.delete_category(category_id)

        if result.ok:
            logger.debug("Category deleted: %s", category_id)
            
        else:
            logger.warning("Failed to delete category %s: %s", category_id, result.error)

        return result
