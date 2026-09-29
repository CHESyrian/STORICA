"""
ExampleController — inventory screen controller.

Pulls the shared InventoryClient from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class ExampleController:

    def __init__(self):
        # Single line — no api_client argument, no InventoryService wrapper.
        self.inventory = Services.inventory

    # ------------------------------------------------------------------
    # Example
    # ------------------------------------------------------------------

    def load_examples(
        self,
        page: int = 1,
        search: str | None = None,
        active: bool | None = True, 
        category: str | None = None,
        unit: str | None = None
    ) -> APIResult:
        """
        Fetch the product list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.inventory.list_examples(
            page=page,
            search=search,
            active=active, 
            category=category, 
            unit=unit
        )

        if result.ok:
            logger.debug(
                "Example loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
            
        else:
            logger.warning("Failed to load examples: %s", result.error)

        return result

    # ..etc

