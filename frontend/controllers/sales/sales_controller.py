"""
SalesController — sales screen controller.

Pulls the shared SalesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any, Literal

from frontend.services import Services

from frontend.api import APIResult

from frontend.utils.constants import (
    ORDER_STATUS, 
    INVOICE_STATUS
)


logger = logging.getLogger(__name__)


class SalesController:

    def __init__(self):
        # Single line — no api_client argument, no SalesService wrapper.
        self.sales = Services.sales

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        return self.sales.get_all(model)

    # ------------------------------------------------------------------
    # Customers
    # ------------------------------------------------------------------
    def load_customers(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the customer list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.sales.list_customers(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active or None,
            is_verified=is_verified,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Customers loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )

        else:
            logger.warning("Failed to load customers: %s", result.error)

        return result

    def create_customer(self, customer_data: dict[str, Any]) -> APIResult:
        """Create a new customer."""
        result = self.sales.create_customer(customer_data)

        if result.ok:
            logger.debug("Customer created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create customer: %s", result.error)

        return result

    def get_customer(self, customer_id: int) -> APIResult:
        """Retrieve a specific customer."""
        result = self.sales.get_customer(customer_id)

        if result.ok:
            logger.debug("Customer loaded: %s", customer_id)

        else:
            logger.warning("Failed to load customer %s: %s", customer_id, result.error)

        return result

    def update_customer(self, customer_id: int, customer_data: dict[str, Any]) -> APIResult:
        """Fully update a customer."""
        result = self.sales.update_customer(customer_id, customer_data)

        if result.ok:
            logger.debug("Customer updated: %s", customer_id)

        else:
            logger.warning("Failed to update customer %s: %s", customer_id, result.error)

        return result

    def partial_update_customer(self, customer_id: int, customer_data: dict[str, Any]) -> APIResult:
        """Partially update a customer."""
        result = self.sales.partial_update_customer(customer_id, customer_data)

        if result.ok:
            logger.debug("Customer partially updated: %s", customer_id)

        else:
            logger.warning("Failed to partially update customer %s: %s", customer_id, result.error)

        return result

    def delete_customer(self, customer_id: int) -> APIResult:
        """Delete a customer."""
        result = self.sales.delete_customer(customer_id)

        if result.ok:
            logger.debug("Customer deleted: %s", customer_id)

        else:
            logger.warning("Failed to delete customer %s: %s", customer_id, result.error)

        return result


    # ------------------------------------------------------------------
    # Sales Orders
    # ------------------------------------------------------------------
    def load_sales_orders(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal[
            tuple(code for code, _ in ORDER_STATUS)
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
        customer: int | None = None,
    ) -> APIResult:
        """
        Fetch the sales order list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.sales.list_sales_orders(
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            customer=customer,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Sales orders loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )

        else:
            logger.warning("Failed to load sales orders: %s", result.error)

        return result

    def create_sales_order(self, order_data: dict[str, Any]) -> APIResult:
        """Create a new sales order."""
        result = self.sales.create_sales_order(order_data)

        if result.ok:
            logger.debug("Sales order created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create sales order: %s", result.error)

        return result

    def get_sales_order(self, order_id: int) -> APIResult:
        """Retrieve a specific sales order."""
        result = self.sales.get_sales_order(order_id)

        if result.ok:
            logger.debug("Sales order loaded: %s", order_id)

        else:
            logger.warning("Failed to load sales order %s: %s", order_id, result.error)

        return result

    def update_sales_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """Fully update a sales order."""
        result = self.sales.update_sales_order(order_id, order_data)

        if result.ok:
            logger.debug("Sales order updated: %s", order_id)

        else:
            logger.warning("Failed to update sales order %s: %s", order_id, result.error)

        return result

    def partial_update_sales_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """Partially update a sales order."""
        result = self.sales.partial_update_sales_order(order_id, order_data)

        if result.ok:
            logger.debug("Sales order partially updated: %s", order_id)

        else:
            logger.warning("Failed to partially update sales order %s: %s", order_id, result.error)

        return result

    def delete_sales_order(self, order_id: int) -> APIResult:
        """Delete a sales order."""
        result = self.sales.delete_sales_order(order_id)

        if result.ok:
            logger.debug("Sales order deleted: %s", order_id)

        else:
            logger.warning("Failed to delete sales order %s: %s", order_id, result.error)

        return result

    def cancel_sales_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Cancel a sales order."""
        result = self.sales.cancel_sales_order(order_id, data)

        if result.ok:
            logger.debug("Sales order cancelled: %s", order_id)

        else:
            logger.warning("Failed to cancel sales order %s: %s", order_id, result.error)

        return result

    def confirm_sales_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Confirm a draft sales order."""
        result = self.sales.confirm_sales_order(order_id, data)
        if result.ok:
            logger.debug("Sales order confirmed: %s", order_id)
        else:
            logger.warning("Failed to confirm sales order %s: %s", order_id, result.error)
        return result

    def complete_sales_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Complete a sales order."""
        result = self.sales.complete_sales_order(order_id, data)
        if result.ok:
            logger.debug("Sales order completed: %s", order_id)
        else:
            logger.warning("Failed to complete sales order %s: %s", order_id, result.error)
        return result

    # ------------------------------------------------------------------
    # Sales Invoices
    # ------------------------------------------------------------------
    def load_sales_invoices(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal[
            tuple(code for code, _ in INVOICE_STATUS)
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
        customer: int | None = None,
        order: int | None = None,
    ) -> APIResult:
        """
        Fetch the sales invoice list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.sales.list_sales_invoices(
            page=page,
            page_size=page_size,
            search=search,
            customer=customer,
            order=order,
            status=status,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Sales invoices loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )

        else:
            logger.warning("Failed to load sales invoices: %s", result.error)

        return result

    def create_sales_invoice(self, invoice_data: dict[str, Any]) -> APIResult:
        """Create a new sales invoice."""
        result = self.sales.create_sales_invoice(invoice_data)

        if result.ok:
            logger.debug("Sales invoice created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create sales invoice: %s", result.error)

        return result

    def get_sales_invoice(self, invoice_id: int) -> APIResult:
        """Retrieve a specific sales invoice."""
        result = self.sales.get_sales_invoice(invoice_id)

        if result.ok:
            logger.debug("Sales invoice loaded: %s", invoice_id)

        else:
            logger.warning("Failed to load sales invoice %s: %s", invoice_id, result.error)

        return result

    def update_sales_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """Fully update a sales invoice."""
        result = self.sales.update_sales_invoice(invoice_id, invoice_data)

        if result.ok:
            logger.debug("Sales invoice updated: %s", invoice_id)

        else:
            logger.warning("Failed to update sales invoice %s: %s", invoice_id, result.error)

        return result

    def partial_update_sales_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """Partially update a sales invoice."""
        result = self.sales.partial_update_sales_invoice(invoice_id, invoice_data)

        if result.ok:
            logger.debug("Sales invoice partially updated: %s", invoice_id)

        else:
            logger.warning(
                "Failed to partially update sales invoice %s: %s", invoice_id, result.error
            )

        return result

    def delete_sales_invoice(self, invoice_id: int) -> APIResult:
        """Delete a sales invoice."""
        result = self.sales.delete_sales_invoice(invoice_id)

        if result.ok:
            logger.debug("Sales invoice deleted: %s", invoice_id)

        else:
            logger.warning("Failed to delete sales invoice %s: %s", invoice_id, result.error)

        return result

    def post_sales_invoice(self, invoice_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Post a sales invoice."""
        result = self.sales.post_sales_invoice(invoice_id, data)

        if result.ok:
            logger.debug("Sales invoice posted: %s", invoice_id)

        else:
            logger.warning("Failed to post sales invoice %s: %s", invoice_id, result.error)

        return result

    def cancel_sales_invoice(self, invoice_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Cancel a sales invoice."""
        result = self.sales.cancel_sales_invoice(invoice_id, data)
        if result.ok:
            logger.debug("Sales invoice cancelled: %s", invoice_id)
        else:
            logger.warning("Failed to cancel sales invoice %s: %s", invoice_id, result.error)
        return result

    # ------------------------------------------------------------------
    # Sales Payments
    # ------------------------------------------------------------------

    def load_sales_payments(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: str | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """Fetch sales payment list."""
        result = self.sales.list_sales_payments(
            page=page,
            page_size=page_size,
            search=search,
            status=status,
            ordering=ordering,
        )
        if result.ok:
            logger.debug("Sales payments loaded")
        else:
            logger.warning("Failed to load sales payments: %s", result.error)
        return result

    def get_sales_payment(self, payment_id: int) -> APIResult:
        """Retrieve a specific sales payment."""
        result = self.sales.get_sales_payment(payment_id)
        if result.ok:
            logger.debug("Sales payment loaded: %s", payment_id)
        else:
            logger.warning(
                "Failed to load sales payment %s: %s",
                payment_id,
                result.error,
            )
        return result

    def create_sales_payment(self, payment_data: dict) -> APIResult:
        result = self.sales.create_sales_payment(payment_data)
        if result.ok:
            logger.debug("Sales payment created")
        else:
            logger.warning("Failed to create sales payment: %s", result.error)
        return result

    def delete_sales_payment(self, payment_id: int) -> APIResult:
        result = self.sales.delete_sales_payment(payment_id)
        if result.ok:
            logger.debug("Sales payment deleted: %s", payment_id)
        else:
            logger.warning(
                "Failed to delete sales payment %s: %s",
                payment_id,
                result.error,
            )
        return result

    def refund_sales_payment(self, payment_id: int, data: dict | None = None) -> APIResult:
        """Refund a sales payment and adjust invoice balance."""
        result = self.sales.refund_sales_payment(payment_id, data)
        if result.ok:
            logger.debug("Sales payment refunded: %s", payment_id)
        else:
            logger.warning(
                "Failed to refund sales payment %s: %s",
                payment_id,
                result.error,
            )
        return result
