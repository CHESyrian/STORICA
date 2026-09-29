"""
frontend/api/purchases_service.py

All API calls for the Purchases module (suppliers, orders, invoices, payments).

This client does NOT extend APIClient — it receives the shared AuthClient
and delegates every request through it.
"""

from __future__ import annotations

import logging
from typing import Literal, Any

from frontend.api.auth_client import AuthClient
from frontend.api.base_client import APIResult

logger = logging.getLogger(__name__)


class PurchasesService:
    """API client for purchases / procurement endpoints."""

    def __init__(self, auth_client: AuthClient) -> None:
        self._client = auth_client

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        """GET /api/model/ - Retrieve all records."""
        return self._client.get(f"/{model}/all/")

    # ------------------------------------------------------------------
    # Suppliers
    # ------------------------------------------------------------------

    def list_suppliers(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/suppliers/ - List suppliers with optional filters."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search

        if is_active is not None:
            params["is_active"] = str(is_active).lower()

        if is_verified is not None:
            params["is_verified"] = str(is_verified).lower()

        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/suppliers/", params=params)

    def create_supplier(self, supplier_data: dict[str, Any]) -> APIResult:
        """POST /api/suppliers/ - Create a new supplier."""
        return self._client.post("/suppliers/", data=supplier_data)

    def get_supplier(self, supplier_id: int) -> APIResult:
        """GET /api/suppliers/{id}/ - Retrieve a specific supplier."""
        return self._client.get(f"/suppliers/{supplier_id}/")

    def update_supplier(self, supplier_id: int, supplier_data: dict[str, Any]) -> APIResult:
        """PUT /api/suppliers/{id}/ - Fully update a supplier."""
        return self._client.put(f"/suppliers/{supplier_id}/", data=supplier_data)

    def partial_update_supplier(self, supplier_id: int, supplier_data: dict[str, Any]) -> APIResult:
        """PATCH /api/suppliers/{id}/ - Partially update a supplier."""
        return self._client.patch(f"/suppliers/{supplier_id}/", data=supplier_data)

    def delete_supplier(self, supplier_id: int) -> APIResult:
        """DELETE /api/suppliers/{id}/ - Delete a supplier."""
        return self._client.delete(f"/suppliers/{supplier_id}/")

    # ------------------------------------------------------------------
    # Purchase Orders
    # ------------------------------------------------------------------

    def list_purchase_orders(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal[
            "cancelled", "completed", "confirmed", "delivered",
            "draft", "processing", "returned", "shipped"
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
        supplier: int | None = None,
    ) -> APIResult:
        """GET /api/purchases-orders/ - List purchase orders with optional filters."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search

        if status is not None:
            params["status"] = status

        if is_active is not None:
            params["is_active"] = str(is_active).lower()

        if ordering is not None:
            params["ordering"] = ordering

        if supplier is not None:
            params["supplier"] = supplier

        return self._client.get("/purchases-orders/", params=params)

    def create_purchase_order(self, order_data: dict[str, Any]) -> APIResult:
        """POST /api/purchases-orders/ - Create a new purchase order."""
        return self._client.post("/purchases-orders/", data=order_data)

    def get_purchase_order(self, order_id: int) -> APIResult:
        """GET /api/purchases-orders/{id}/ - Retrieve a specific purchase order."""
        return self._client.get(f"/purchases-orders/{order_id}/")

    def update_purchase_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """PUT /api/purchases-orders/{id}/ - Fully update a purchase order."""
        return self._client.put(f"/purchases-orders/{order_id}/", data=order_data)

    def partial_update_purchase_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """PATCH /api/purchases-orders/{id}/ - Partially update a purchase order."""
        return self._client.patch(f"/purchases-orders/{order_id}/", data=order_data)

    def delete_purchase_order(self, order_id: int) -> APIResult:
        """DELETE /api/purchases-orders/{id}/ - Delete a purchase order."""
        return self._client.delete(f"/purchases-orders/{order_id}/")

    def cancel_purchase_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/purchases-orders/{id}/cancel/ - Cancel a purchase order."""
        return self._client.post(f"/purchases-orders/{order_id}/cancel/", data=data or {})

    def confirm_purchase_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/purchases-orders/{id}/confirm/ - Confirm a draft purchase order."""
        return self._client.post(f"/purchases-orders/{order_id}/confirm/", data=data or {})

    def complete_purchase_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/purchases-orders/{id}/complete/ - Complete a purchase order."""
        return self._client.post(f"/purchases-orders/{order_id}/complete/", data=data or {})

    # ------------------------------------------------------------------
    # Purchase Order Items
    # ------------------------------------------------------------------

    def list_purchase_order_items(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        ordering: str | None = None,
        order: int | None = None,
        variant: int | None = None,
    ) -> APIResult:
        """GET /api/purchases-order-items/ - List purchase order items."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search

        if ordering is not None:
            params["ordering"] = ordering

        if order is not None:
            params["order"] = order

        if variant is not None:
            params["variant"] = variant
            

        return self._client.get("/purchases-order-items/", params=params)

    def create_purchase_order_item(self, item_data: dict[str, Any]) -> APIResult:
        """POST /api/purchases-order-items/ - Create a new purchase order item."""
        return self._client.post("/purchases-order-items/", data=item_data)

    def get_purchase_order_item(self, item_id: int) -> APIResult:
        """GET /api/purchases-order-items/{id}/ - Retrieve a specific order item."""
        return self._client.get(f"/purchases-order-items/{item_id}/")

    def update_purchase_order_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """PUT /api/purchases-order-items/{id}/ - Fully update an order item."""
        return self._client.put(f"/purchases-order-items/{item_id}/", data=item_data)

    def partial_update_purchase_order_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """PATCH /api/purchases-order-items/{id}/ - Partially update an order item."""
        return self._client.patch(f"/purchases-order-items/{item_id}/", data=item_data)

    def delete_purchase_order_item(self, item_id: int) -> APIResult:
        """DELETE /api/purchases-order-items/{id}/ - Delete an order item."""
        return self._client.delete(f"/purchases-order-items/{item_id}/")

    # ------------------------------------------------------------------
    # Purchase Invoices
    # ------------------------------------------------------------------

    def list_purchase_invoices(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal[
            "cancelled", "draft", "overdue", "paid", "partial", "refunded", "sent"
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
        supplier: int | None = None,
        order: int | None = None,
    ) -> APIResult:
        """GET /api/purchases-invoices/ - List purchase invoices with filters."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search

        if status is not None:
            params["status"] = status

        if is_active is not None:
            params["is_active"] = str(is_active).lower()
            
        if ordering is not None:
            params["ordering"] = ordering

        if supplier is not None:
            params["supplier"] = supplier

        if order is not None:
            params["order"] = order

        return self._client.get("/purchases-invoices/", params=params)

    def create_purchase_invoice(self, invoice_data: dict[str, Any]) -> APIResult:
        """POST /api/purchases-invoices/ - Create a new purchase invoice."""
        return self._client.post("/purchases-invoices/", data=invoice_data)

    def get_purchase_invoice(self, invoice_id: int) -> APIResult:
        """GET /api/purchases-invoices/{id}/ - Retrieve a specific invoice."""
        return self._client.get(f"/purchases-invoices/{invoice_id}/")

    def update_purchase_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """PUT /api/purchases-invoices/{id}/ - Fully update an invoice."""
        return self._client.put(f"/purchases-invoices/{invoice_id}/", data=invoice_data)

    def partial_update_purchase_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """PATCH /api/purchases-invoices/{id}/ - Partially update an invoice."""
        return self._client.patch(f"/purchases-invoices/{invoice_id}/", data=invoice_data)

    def delete_purchase_invoice(self, invoice_id: int) -> APIResult:
        """DELETE /api/purchases-invoices/{id}/ - Delete an invoice."""
        return self._client.delete(f"/purchases-invoices/{invoice_id}/")

    def post_purchase_invoice(self, invoice_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/purchases-invoices/{id}/post/ - Idempotent (stock received on create)."""
        return self._client.post(f"/purchases-invoices/{invoice_id}/post/", data=data or {})

    def cancel_purchase_invoice(self, invoice_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/purchases-invoices/{id}/cancel/ - Cancel a purchase invoice."""
        return self._client.post(f"/purchases-invoices/{invoice_id}/cancel/", data=data or {})

    # ------------------------------------------------------------------
    # Purchase Invoice Items
    # ------------------------------------------------------------------

    def list_purchase_invoice_items(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        ordering: str | None = None,
        invoice: int | None = None,
        variant: int | None = None,
    ) -> APIResult:
        """GET /api/purchases-invoice-items/ - List purchase invoice items."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search
            
        if ordering is not None:
            params["ordering"] = ordering

        if invoice is not None:
            params["invoice"] = invoice

        if variant is not None:
            params["variant"] = variant

        return self._client.get("/purchases-invoice-items/", params=params)

    def create_purchase_invoice_item(self, item_data: dict[str, Any]) -> APIResult:
        """POST /api/purchases-invoice-items/ - Create a new invoice item."""
        return self._client.post("/purchases-invoice-items/", data=item_data)

    def get_purchase_invoice_item(self, item_id: int) -> APIResult:
        """GET /api/purchases-invoice-items/{id}/ - Retrieve an invoice item."""
        return self._client.get(f"/purchases-invoice-items/{item_id}/")

    def update_purchase_invoice_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """PUT /api/purchases-invoice-items/{id}/ - Fully update an invoice item."""
        return self._client.put(f"/purchases-invoice-items/{item_id}/", data=item_data)

    def partial_update_purchase_invoice_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """PATCH /api/purchases-invoice-items/{id}/ - Partially update an invoice item."""
        return self._client.patch(f"/purchases-invoice-items/{item_id}/", data=item_data)

    def delete_purchase_invoice_item(self, item_id: int) -> APIResult:
        """DELETE /api/purchases-invoice-items/{id}/ - Delete an invoice item."""
        return self._client.delete(f"/purchases-invoice-items/{item_id}/")

    # ------------------------------------------------------------------
    # Purchase Payments
    # ------------------------------------------------------------------

    def list_purchase_payments(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal["completed", "failed", "partial", "pending", "refunded"] | None = None,
        ordering: str | None = None,
        supplier: int | None = None,
        order: int | None = None,
        invoice: int | None = None,
    ) -> APIResult:
        """GET /api/purchases-payments/ - List purchase payments with filters."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search

        if status is not None:
            params["status"] = status

        if ordering is not None:
            params["ordering"] = ordering

        if supplier is not None:
            params["supplier"] = supplier

        if order is not None:
            params["order"] = order

        if invoice is not None:
            params["invoice"] = invoice

        return self._client.get("/purchases-payments/", params=params)

    def create_purchase_payment(self, payment_data: dict[str, Any]) -> APIResult:
        """POST /api/purchases-payments/ - Create a new purchase payment."""
        return self._client.post("/purchases-payments/", data=payment_data)

    def get_purchase_payment(self, payment_id: int) -> APIResult:
        """GET /api/purchases-payments/{id}/ - Retrieve a specific payment."""
        return self._client.get(f"/purchases-payments/{payment_id}/")

    def update_purchase_payment(self, payment_id: int, payment_data: dict[str, Any]) -> APIResult:
        """PUT /api/purchases-payments/{id}/ - Fully update a payment."""
        return self._client.put(f"/purchases-payments/{payment_id}/", data=payment_data)

    def partial_update_purchase_payment(self, payment_id: int, payment_data: dict[str, Any]) -> APIResult:
        """PATCH /api/purchases-payments/{id}/ - Partially update a payment."""
        return self._client.patch(f"/purchases-payments/{payment_id}/", data=payment_data)

    def delete_purchase_payment(self, payment_id: int) -> APIResult:
        """DELETE /api/purchases-payments/{id}/ - Delete a payment."""
        return self._client.delete(f"/purchases-payments/{payment_id}/")

    def refund_purchase_payment(self, payment_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/purchases-payments/{id}/refund/ - Refund a payment."""
        return self._client.post(f"/purchases-payments/{payment_id}/refund/", data=data or {})


