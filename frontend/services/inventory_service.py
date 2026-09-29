"""
frontend/api/inventory_service.py

All API calls for the Inventory module (warehouses, categories, products, variants, stock movements).

This client does NOT extend APIClient — it receives the shared AuthClient
and delegates every request through it.
"""

from __future__ import annotations

import logging
from typing import Literal, Any

from frontend.api.auth_client import AuthClient
from frontend.api.base_client import APIResult

logger = logging.getLogger(__name__)


class InventoryService:
    """API client for inventory / product endpoints."""

    def __init__(self, auth_client: AuthClient) -> None:
        self._client = auth_client

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        """GET /api/model/ - Retrieve all records."""
        return self._client.get(f"/{model}/all/")

    # ------------------------------------------------------------------
    # Products
    # ------------------------------------------------------------------
    def list_products(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        category: int | None = None,
        unit: str | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/products/ - List products with optional filters."""

        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search

        if category is not None:
            params["category"] = category

        if unit is not None:
            params["unit"] = unit

        if is_active is not None:
            params["is_active"] = str(is_active).lower()

        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/products/", params=params)

    def create_product(self, product_data: dict[str, Any]) -> APIResult:
        """POST /api/products/ - Create a new product."""
        return self._client.post("/products/", data=product_data)

    def get_product(self, product_id: int) -> APIResult:
        """GET /api/products/{id}/ - Retrieve a specific product."""
        return self._client.get(f"/products/{product_id}/")

    def update_product(
        self, 
        product_id: int, 
        product_data: dict[str, Any]
    ) -> APIResult:
        """PUT /api/products/{id}/ - Fully update a product."""
        return self._client.put(f"/products/{product_id}/", data=product_data)

    def partial_update_product(
        self, 
        product_id: int, 
        product_data: dict[str, Any]
    ) -> APIResult:
        """PATCH /api/products/{id}/ - Partially update a product."""
        return self._client.patch(f"/products/{product_id}/", data=product_data)

    def delete_product(self, product_id: int) -> APIResult:
        """DELETE /api/products/{id}/ - Delete a product."""
        return self._client.delete(f"/products/{product_id}/")

    # ------------------------------------------------------------------
    # Warehouses
    # ------------------------------------------------------------------
    def list_warehouses(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal["active", "inactive", "maintenance"] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/warehouses/ - List warehouses with optional filters."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search

        if status is not None:
            params["status"] = status

        if is_active is not None:
            params["is_active"] = str(is_active).lower()

        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/warehouses/", params=params)

    def create_warehouse(self, warehouse_data: dict[str, Any]) -> APIResult:
        """POST /api/warehouses/ - Create a new warehouse."""
        return self._client.post("/warehouses/", data=warehouse_data)

    def get_warehouse(self, warehouse_id: int) -> APIResult:
        """GET /api/warehouses/{id}/ - Retrieve a specific warehouse."""
        return self._client.get(f"/warehouses/{warehouse_id}/")

    def update_warehouse(
        self, 
        warehouse_id: int, 
        warehouse_data: dict[str, Any]
    ) -> APIResult:
        """PUT /api/warehouses/{id}/ - Fully update a warehouse."""
        return self._client.put(
            f"/warehouses/{warehouse_id}/", 
            data=warehouse_data
        )

    def partial_update_warehouse(
        self, 
        warehouse_id: int, 
        warehouse_data: dict[str, Any]
    ) -> APIResult:
        """PATCH /api/warehouses/{id}/ - Partially update a warehouse."""
        return self._client.patch(
            f"/warehouses/{warehouse_id}/", 
            data=warehouse_data
        )

    def delete_warehouse(self, warehouse_id: int) -> APIResult:
        """DELETE /api/warehouses/{id}/ - Delete a warehouse."""
        return self._client.delete(f"/warehouses/{warehouse_id}/")

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------
    def list_categories(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        parent: int | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/categories/ - List categories with optional filters."""
        params: dict = {"page": page, "page_size": page_size}

        if search is not None:
            params["search"] = search

        if parent is not None:
            params["parent"] = parent

        if is_active is not None:
            params["is_active"] = str(is_active).lower()

        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/categories/", params=params)

    def create_category(self, category_data: dict[str, Any]) -> APIResult:
        """POST /api/categories/ - Create a new category."""
        return self._client.post("/categories/", data=category_data)

    def get_category(self, category_id: int) -> APIResult:
        """GET /api/categories/{id}/ - Retrieve a specific category."""
        return self._client.get(f"/categories/{category_id}/")

    def update_category(self, category_id: int, category_data: dict[str, Any]) -> APIResult:
        """PUT /api/categories/{id}/ - Fully update a category."""
        return self._client.put(f"/categories/{category_id}/", data=category_data)

    def partial_update_category(self, category_id: int, category_data: dict[str, Any]) -> APIResult:
        """PATCH /api/categories/{id}/ - Partially update a category."""
        return self._client.patch(f"/categories/{category_id}/", data=category_data)

    def delete_category(self, category_id: int) -> APIResult:
        """DELETE /api/categories/{id}/ - Delete a category."""
        return self._client.delete(f"/categories/{category_id}/")

    # ------------------------------------------------------------------
    # Variants
    # ------------------------------------------------------------------
    def list_variants(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        product: int | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/variants/ - List variants with optional filters."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search

        if product is not None:
            params["product"] = product

        if is_active is not None:
            params["is_active"] = str(is_active).lower()

        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/variants/", params=params)

    def create_variant(self, variant_data: dict[str, Any]) -> APIResult:
        """POST /api/variants/ - Create a new variant."""
        return self._client.post("/variants/", data=variant_data)

    def get_variant(self, variant_id: int) -> APIResult:
        """GET /api/variants/{id}/ - Retrieve a specific variant."""
        return self._client.get(f"/variants/{variant_id}/")

    def update_variant(self, variant_id: int, variant_data: dict[str, Any]) -> APIResult:
        """PUT /api/variants/{id}/ - Fully update a variant."""
        return self._client.put(f"/variants/{variant_id}/", data=variant_data)

    def partial_update_variant(self, variant_id: int, variant_data: dict[str, Any]) -> APIResult:
        """PATCH /api/variants/{id}/ - Partially update a variant."""
        return self._client.patch(f"/variants/{variant_id}/", data=variant_data)

    def delete_variant(self, variant_id: int) -> APIResult:
        """DELETE /api/variants/{id}/ - Delete a variant."""
        return self._client.delete(f"/variants/{variant_id}/")

    # ------------------------------------------------------------------
    # Stock Movements
    # ------------------------------------------------------------------
    def list_stock_movements(
        self,
        *,
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
        """GET /api/stock-movements/ - List stock movements with optional filters."""
        params: dict = {"page": page, "page_size": page_size}

        if search is not None:
            params["search"] = search

        if movement_type is not None:
            params["movement_type"] = movement_type

        if status is not None:
            params["status"] = status

        if product is not None:
            params["product"] = product

        if batch is not None:
            params["batch"] = batch

        if performed_by is not None:
            params["performed_by"] = performed_by

        if from_warehouse is not None:
            params["from_warehouse"] = from_warehouse

        if to_warehouse is not None:
            params["to_warehouse"] = to_warehouse

        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/stock-movements/", params=params)

    def create_stock_movement(self, movement_data: dict[str, Any]) -> APIResult:
        """POST /api/stock-movements/ - Create a new stock movement."""
        return self._client.post("/stock-movements/", data=movement_data)

    def get_stock_movement(self, movement_id: int) -> APIResult:
        """GET /api/stock-movements/{id}/ - Retrieve a specific stock movement."""
        return self._client.get(f"/stock-movements/{movement_id}/")

    def update_stock_movement(self, movement_id: int, movement_data: dict[str, Any]) -> APIResult:
        """PUT /api/stock-movements/{id}/ - Fully update a stock movement."""
        return self._client.put(f"/stock-movements/{movement_id}/", data=movement_data)

    def partial_update_stock_movement(self, movement_id: int, movement_data: dict[str, Any]) -> APIResult:
        """PATCH /api/stock-movements/{id}/ - Partially update a stock movement."""
        return self._client.patch(f"/stock-movements/{movement_id}/", data=movement_data)

    def delete_stock_movement(self, movement_id: int) -> APIResult:
        """DELETE /api/stock-movements/{id}/ - Delete a stock movement."""
        return self._client.delete(f"/stock-movements/{movement_id}/")


    # ------------------------------------------------------------------
    # Batches
    # ------------------------------------------------------------------
    def list_batches(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal["active", "expired", "recalled", "sold_out"] | None = None, 
        is_active: bool | None = None,
        ordering: str | None = None,
        variant: int | None = None,
        warehouse: int | None = None,
    ) -> APIResult:
        """GET /api/batches/ - List batches with optional filters."""
        params: dict = {"page": page, "page_size": page_size}

        if search is not None:
            params["search"] = search

        if status is not None:
            params["status"] = status

        if is_active is not None:
            params["is_active"] = str(is_active).lower()

        if ordering is not None:
            params["ordering"] = ordering

        if variant is not None:
            params["variant"] = variant

        if warehouse is not None:
            params["warehouse"] = warehouse

        return self._client.get("/batches/", params=params)

    def create_batch(self, batch_data: dict[str, Any]) -> APIResult:
        """POST /api/batches/ - Create a new batch."""
        return self._client.post("/batches/", data=batch_data)

    def get_batch(self, batch_id: int) -> APIResult:
        """GET /api/batches/{id}/ - Retrieve a specific batch."""
        return self._client.get(f"/batches/{batch_id}/")

    def update_batch(self, batch_id: int, batch_data: dict[str, Any]) -> APIResult:
        """PUT /api/batches/{id}/ - Fully update a batch."""
        return self._client.put(f"/batches/{batch_id}/", data=batch_data)

    def partial_update_batch(self, batch_id: int, batch_data: dict[str, Any]) -> APIResult:
        """PATCH /api/batches/{id}/ - Partially update a batch."""
        return self._client.patch(f"/batches/{batch_id}/", data=batch_data)

    def delete_batch(self, batch_id: int) -> APIResult:
        """DELETE /api/batches/{id}/ - Delete a batch."""
        return self._client.delete(f"/batches/{batch_id}/")

    # ------------------------------------------------------------------
    # Stock Status (aggregated on-hand)
    # ------------------------------------------------------------------
    def list_stock_status(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        warehouse: int | None = None,
        category: int | None = None,
        product: int | None = None,
        variant: int | None = None,
        is_active: bool | None = None,
        zero_stock: bool | None = None,
        low_stock: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/stock-status/ - Aggregated stock by variant × warehouse."""
        params: dict = {"page": page, "page_size": page_size}

        if search is not None:
            params["search"] = search
        if warehouse is not None:
            params["warehouse"] = warehouse
        if category is not None:
            params["category"] = category
        if product is not None:
            params["product"] = product
        if variant is not None:
            params["variant"] = variant
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        if zero_stock is not None:
            params["zero_stock"] = str(zero_stock).lower()
        if low_stock is not None:
            params["low_stock"] = str(low_stock).lower()
        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/stock-status/", params=params)

    def get_all_stock_status(self) -> APIResult:
        """GET /api/stock-status/all/ - Full stock status list."""
        return self._client.get("/stock-status/all/")

