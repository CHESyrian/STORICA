"""
InventoryController — inventory screen controller.
Pulls the shared InventoryService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any, Literal

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class InventoryController:

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

    # ------------------------------------------------------------------
    # Products
    # ------------------------------------------------------------------
    def load_products(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        category: str | None = None,
        unit: str | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the product list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.inventory.list_products(
            page=page,
            page_size=page_size,
            search=search,
            category=category,
            unit=unit,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Products loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )

        else:
            logger.warning("Failed to load products: %s", result.error)

        return result

    def create_product(self, product_data: dict[str, Any]) -> APIResult:
        """Create a new product."""
        result = self.inventory.create_product(product_data)

        if result.ok:
            logger.debug("Product created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create product: %s", result.error)

        return result

    def get_product(self, product_id: int) -> APIResult:
        """Retrieve a specific product."""
        result = self.inventory.get_product(product_id)

        if result.ok:
            logger.debug("Product loaded: %s", product_id)

        else:
            logger.warning("Failed to load product %s: %s", product_id, result.error)

        return result

    def update_product(self, product_id: int, product_data: dict[str, Any]) -> APIResult:
        """Fully update a product."""
        result = self.inventory.update_product(product_id, product_data)

        if result.ok:
            logger.debug("Product updated: %s", product_id)

        else:
            logger.warning("Failed to update product %s: %s", product_id, result.error)

        return result

    def partial_update_product(self, product_id: int, product_data: dict[str, Any]) -> APIResult:
        """Partially update a product."""
        result = self.inventory.partial_update_product(product_id, product_data)

        if result.ok:
            logger.debug("Product partially updated: %s", product_id)

        else:
            logger.warning("Failed to partially update product %s: %s", product_id, result.error)

        return result

    def delete_product(self, product_id: int) -> APIResult:
        """Delete a product."""
        result = self.inventory.delete_product(product_id)

        if result.ok:
            logger.debug("Product deleted: %s", product_id)

        else:
            logger.warning("Failed to delete product %s: %s", product_id, result.error)

        return result


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


