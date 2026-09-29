"""
frontend/api/sales_service.py

All API calls for the Sales module (customers, orders, invoices, payments).

This client does NOT extend APIClient — it receives the shared AuthClient
and delegates every request through it.
"""

from __future__ import annotations

import logging
from typing import Literal, Any

from frontend.api.auth_client import AuthClient
from frontend.api.base_client import APIResult

logger = logging.getLogger(__name__)


class SalesService:
    """API client for sales / customer endpoints."""

    def __init__(self, auth_client: AuthClient) -> None:
        self._client = auth_client

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        """GET /api/model/ - Retrieve all records."""
        return self._client.get(f"/{model}/all/")

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------

    def list_customers(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/customers/ - List customers with optional filters."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        if is_verified is not None:
            params["is_verified"] = str(is_verified).lower()
        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/customers/", params=params)

    def create_customer(self, customer_data: dict[str, Any]) -> APIResult:
        """POST /api/customers/ - Create a new customer."""
        return self._client.post("/customers/", data=customer_data)

    def get_customer(self, customer_id: int) -> APIResult:
        """GET /api/customers/{id}/ - Retrieve a specific customer."""
        return self._client.get(f"/customers/{customer_id}/")

    def update_customer(self, customer_id: int, customer_data: dict[str, Any]) -> APIResult:
        """PUT /api/customers/{id}/ - Fully update a customer."""
        return self._client.put(f"/customers/{customer_id}/", data=customer_data)

    def partial_update_customer(self, customer_id: int, customer_data: dict[str, Any]) -> APIResult:
        """PATCH /api/customers/{id}/ - Partially update a customer."""
        return self._client.patch(f"/customers/{customer_id}/", data=customer_data)

    def delete_customer(self, customer_id: int) -> APIResult:
        """DELETE /api/customers/{id}/ - Delete a customer."""
        return self._client.delete(f"/customers/{customer_id}/")

    # ------------------------------------------------------------------
    # Sales Orders
    # ------------------------------------------------------------------

    def list_sales_orders(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        customer: int | None = None,
        status: Literal[
            "cancelled", "completed", "confirmed", "delivered",
            "draft", "processing", "returned", "shipped"
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/sales-orders/ - List sales orders with optional filters."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search
        if customer is not None:
            params["customer"] = customer
        if status is not None:
            params["status"] = status
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/sales-orders/", params=params)

    def create_sales_order(self, order_data: dict[str, Any]) -> APIResult:
        """POST /api/sales-orders/ - Create a new sales order."""
        return self._client.post("/sales-orders/", data=order_data)

    def get_sales_order(self, order_id: int) -> APIResult:
        """GET /api/sales-orders/{id}/ - Retrieve a specific sales order."""
        return self._client.get(f"/sales-orders/{order_id}/")

    def update_sales_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """PUT /api/sales-orders/{id}/ - Fully update a sales order."""
        return self._client.put(f"/sales-orders/{order_id}/", data=order_data)

    def partial_update_sales_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """PATCH /api/sales-orders/{id}/ - Partially update a sales order."""
        return self._client.patch(f"/sales-orders/{order_id}/", data=order_data)

    def delete_sales_order(self, order_id: int) -> APIResult:
        """DELETE /api/sales-orders/{id}/ - Delete a sales order."""
        return self._client.delete(f"/sales-orders/{order_id}/")

    def cancel_sales_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/sales-orders/{id}/cancel/ - Cancel a sales order."""
        return self._client.post(f"/sales-orders/{order_id}/cancel/", data=data or {})

    def confirm_sales_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/sales-orders/{id}/confirm/ - Confirm a draft sales order."""
        return self._client.post(f"/sales-orders/{order_id}/confirm/", data=data or {})

    def complete_sales_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/sales-orders/{id}/complete/ - Complete a sales order."""
        return self._client.post(f"/sales-orders/{order_id}/complete/", data=data or {})

    # ------------------------------------------------------------------
    # Sales Order Items
    # ------------------------------------------------------------------

    def list_sales_order_items(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        order: int | None = None,
        variant: int | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/sales-order-items/ - List sales order items."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search
        if order is not None:
            params["order"] = order
        if variant is not None:
            params["variant"] = variant
        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/sales-order-items/", params=params)

    def create_sales_order_item(self, item_data: dict[str, Any]) -> APIResult:
        """POST /api/sales-order-items/ - Create a new sales order item."""
        return self._client.post("/sales-order-items/", data=item_data)

    def get_sales_order_item(self, item_id: int) -> APIResult:
        """GET /api/sales-order-items/{id}/ - Retrieve a specific order item."""
        return self._client.get(f"/sales-order-items/{item_id}/")

    def update_sales_order_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """PUT /api/sales-order-items/{id}/ - Fully update an order item."""
        return self._client.put(f"/sales-order-items/{item_id}/", data=item_data)

    def partial_update_sales_order_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """PATCH /api/sales-order-items/{id}/ - Partially update an order item."""
        return self._client.patch(f"/sales-order-items/{item_id}/", data=item_data)

    def delete_sales_order_item(self, item_id: int) -> APIResult:
        """DELETE /api/sales-order-items/{id}/ - Delete an order item."""
        return self._client.delete(f"/sales-order-items/{item_id}/")

    # ------------------------------------------------------------------
    # Sales Invoices
    # ------------------------------------------------------------------

    def list_sales_invoices(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        customer: int | None = None,
        order: int | None = None,
        status: Literal[
            "cancelled", "draft", "overdue", "paid", "partial", "refunded", "sent"
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/sales-invoices/ - List sales invoices with filters."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search
        if customer is not None:
            params["customer"] = customer
        if order is not None:
            params["order"] = order
        if status is not None:
            params["status"] = status
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/sales-invoices/", params=params)

    def create_sales_invoice(self, invoice_data: dict[str, Any]) -> APIResult:
        """POST /api/sales-invoices/ - Create a new sales invoice."""
        return self._client.post("/sales-invoices/", data=invoice_data)

    def get_sales_invoice(self, invoice_id: int) -> APIResult:
        """GET /api/sales-invoices/{id}/ - Retrieve a specific invoice."""
        return self._client.get(f"/sales-invoices/{invoice_id}/")

    def update_sales_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """PUT /api/sales-invoices/{id}/ - Fully update an invoice."""
        return self._client.put(f"/sales-invoices/{invoice_id}/", data=invoice_data)

    def partial_update_sales_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """PATCH /api/sales-invoices/{id}/ - Partially update an invoice."""
        return self._client.patch(f"/sales-invoices/{invoice_id}/", data=invoice_data)

    def delete_sales_invoice(self, invoice_id: int) -> APIResult:
        """DELETE /api/sales-invoices/{id}/ - Delete an invoice."""
        return self._client.delete(f"/sales-invoices/{invoice_id}/")

    def post_sales_invoice(self, invoice_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/sales-invoices/{id}/post/ - Post a sales invoice."""
        return self._client.post(f"/sales-invoices/{invoice_id}/post/", data=data or {})

    def cancel_sales_invoice(self, invoice_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/sales-invoices/{id}/cancel/ - Cancel a sales invoice."""
        return self._client.post(f"/sales-invoices/{invoice_id}/cancel/", data=data or {})

    # ------------------------------------------------------------------
    # Sales Invoice Items
    # ------------------------------------------------------------------

    def list_sales_invoice_items(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        invoice: int | None = None,
        variant: int | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/sales-invoice-items/ - List sales invoice items."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search
        if invoice is not None:
            params["invoice"] = invoice
        if variant is not None:
            params["variant"] = variant
        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/sales-invoice-items/", params=params)

    def create_sales_invoice_item(self, item_data: dict[str, Any]) -> APIResult:
        """POST /api/sales-invoice-items/ - Create a new invoice item."""
        return self._client.post("/sales-invoice-items/", data=item_data)

    def get_sales_invoice_item(self, item_id: int) -> APIResult:
        """GET /api/sales-invoice-items/{id}/ - Retrieve an invoice item."""
        return self._client.get(f"/sales-invoice-items/{item_id}/")

    def update_sales_invoice_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """PUT /api/sales-invoice-items/{id}/ - Fully update an invoice item."""
        return self._client.put(f"/sales-invoice-items/{item_id}/", data=item_data)

    def partial_update_sales_invoice_item(self, item_id: int, item_data: dict[str, Any]) -> APIResult:
        """PATCH /api/sales-invoice-items/{id}/ - Partially update an invoice item."""
        return self._client.patch(f"/sales-invoice-items/{item_id}/", data=item_data)

    def delete_sales_invoice_item(self, item_id: int) -> APIResult:
        """DELETE /api/sales-invoice-items/{id}/ - Delete an invoice item."""
        return self._client.delete(f"/sales-invoice-items/{item_id}/")

    # ------------------------------------------------------------------
    # Sales Payments
    # ------------------------------------------------------------------

    def list_sales_payments(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        customer: int | None = None,
        order: int | None = None,
        invoice: int | None = None,
        status: Literal["completed", "failed", "partial", "pending", "refunded"] | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """GET /api/sales-payments/ - List sales payments with filters."""
        params: dict = {"page": page, "page_size": page_size}
        if search is not None:
            params["search"] = search
        if customer is not None:
            params["customer"] = customer
        if order is not None:
            params["order"] = order
        if invoice is not None:
            params["invoice"] = invoice
        if status is not None:
            params["status"] = status
        if ordering is not None:
            params["ordering"] = ordering

        return self._client.get("/sales-payments/", params=params)

    def create_sales_payment(self, payment_data: dict[str, Any]) -> APIResult:
        """POST /api/sales-payments/ - Create a new sales payment."""
        return self._client.post("/sales-payments/", data=payment_data)

    def get_sales_payment(self, payment_id: int) -> APIResult:
        """GET /api/sales-payments/{id}/ - Retrieve a specific payment."""
        return self._client.get(f"/sales-payments/{payment_id}/")

    def update_sales_payment(self, payment_id: int, payment_data: dict[str, Any]) -> APIResult:
        """PUT /api/sales-payments/{id}/ - Fully update a payment."""
        return self._client.put(f"/sales-payments/{payment_id}/", data=payment_data)

    def partial_update_sales_payment(self, payment_id: int, payment_data: dict[str, Any]) -> APIResult:
        """PATCH /api/sales-payments/{id}/ - Partially update a payment."""
        return self._client.patch(f"/sales-payments/{payment_id}/", data=payment_data)

    def delete_sales_payment(self, payment_id: int) -> APIResult:
        """DELETE /api/sales-payments/{id}/ - Delete a payment."""
        return self._client.delete(f"/sales-payments/{payment_id}/")

    def refund_sales_payment(self, payment_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """POST /api/sales-payments/{id}/refund/ - Refund a payment."""
        return self._client.post(f"/sales-payments/{payment_id}/refund/", data=data or {})
