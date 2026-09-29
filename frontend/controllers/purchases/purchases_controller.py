"""
PurchasesController — purchases screen controller.

Pulls the shared PurchasesService from the Services singleton.
No auth_client argument needed anywhere in this file.
"""

import logging
from typing import Any, Literal

from frontend.services import Services
from frontend.api import APIResult

from frontend.utils.constants import (
    ORDER_STATUS, 
    INVOICE_STATUS, 
    PAYMENT_STATUS, 
)

logger = logging.getLogger(__name__)


class PurchasesController:

    def __init__(self):
        # Single line — no api_client argument, no PurchasesService wrapper.
        self.purchases = Services.purchases


    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        return self.purchases.get_all(model)


    # ------------------------------------------------------------------
    # Suppliers
    # ------------------------------------------------------------------
    def load_suppliers(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        is_active: bool | None = None,
        is_verified: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        """
        Fetch the supplier list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.purchases.list_suppliers(
            page=page,
            page_size=page_size,
            search=search,
            is_active=is_active or None,
            is_verified=is_verified,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Suppliers loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )

        else:
            logger.warning("Failed to load suppliers: %s", result.error)

        return result

    def create_supplier(self, supplier_data: dict[str, Any]) -> APIResult:
        """Create a new supplier."""
        result = self.purchases.create_supplier(supplier_data)

        if result.ok:
            logger.debug("Supplier created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create supplier: %s", result.error)

        return result

    def get_supplier(self, supplier_id: int) -> APIResult:
        """Retrieve a specific supplier."""
        result = self.purchases.get_supplier(supplier_id)

        if result.ok:
            logger.debug("Supplier loaded: %s", supplier_id)

        else:
            logger.warning("Failed to load supplier %s: %s", supplier_id, result.error)

        return result

    def update_supplier(self, supplier_id: int, supplier_data: dict[str, Any]) -> APIResult:
        """Fully update a supplier."""
        result = self.purchases.update_supplier(supplier_id, supplier_data)

        if result.ok:
            logger.debug("Supplier updated: %s", supplier_id)

        else:
            logger.warning("Failed to update supplier %s: %s", supplier_id, result.error)

        return result

    def partial_update_supplier(self, supplier_id: int, supplier_data: dict[str, Any]) -> APIResult:
        """Partially update a supplier."""
        result = self.purchases.partial_update_supplier(supplier_id, supplier_data)

        if result.ok:
            logger.debug("Supplier partially updated: %s", supplier_id)

        else:
            logger.warning("Failed to partially update supplier %s: %s", supplier_id, result.error)

        return result

    def delete_supplier(self, supplier_id: int) -> APIResult:
        """Delete a supplier."""
        result = self.purchases.delete_supplier(supplier_id)

        if result.ok:
            logger.debug("Supplier deleted: %s", supplier_id)

        else:
            logger.warning("Failed to delete supplier %s: %s", supplier_id, result.error)

        return result


    # ------------------------------------------------------------------
    # Purchase Orders
    # ------------------------------------------------------------------
    def load_purchase_orders(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal[
            tuple(code for code, _ in ORDER_STATUS)
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None, 
        supplier: int | None = None,
    ) -> APIResult:
        """
        Fetch the purchase order list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.purchases.list_purchase_orders(
            page=page,
            page_size=page_size,
            search=search,
            supplier=supplier,
            status=status,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Purchase orders loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load purchase orders: %s", result.error)

        return result

    def create_purchase_order(self, order_data: dict[str, Any]) -> APIResult:
        """Create a new purchase order."""
        result = self.purchases.create_purchase_order(order_data)

        if result.ok:
            logger.debug("Purchase order created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create purchase order: %s", result.error)

        return result

    def get_purchase_order(self, order_id: int) -> APIResult:
        """Retrieve a specific purchase order."""
        result = self.purchases.get_purchase_order(order_id)

        if result.ok:
            logger.debug("Purchase order loaded: %s", order_id)

        else:
            logger.warning("Failed to load purchase order %s: %s", order_id, result.error)

        return result

    def update_purchase_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """Fully update a purchase order."""
        result = self.purchases.update_purchase_order(order_id, order_data)

        if result.ok:
            logger.debug("Purchase order updated: %s", order_id)

        else:
            logger.warning("Failed to update purchase order %s: %s", order_id, result.error)

        return result

    def partial_update_purchase_order(self, order_id: int, order_data: dict[str, Any]) -> APIResult:
        """Partially update a purchase order."""
        result = self.purchases.partial_update_purchase_order(order_id, order_data)

        if result.ok:
            logger.debug("Purchase order partially updated: %s", order_id)

        else:
            logger.warning("Failed to partially update purchase order %s: %s", order_id, result.error)

        return result

    def delete_purchase_order(self, order_id: int) -> APIResult:
        """Delete a purchase order."""
        result = self.purchases.delete_purchase_order(order_id)

        if result.ok:
            logger.debug("Purchase order deleted: %s", order_id)

        else:
            logger.warning("Failed to delete purchase order %s: %s", order_id, result.error)

        return result

    def cancel_purchase_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Cancel a purchase order."""
        result = self.purchases.cancel_purchase_order(order_id, data)

        if result.ok:
            logger.debug("Purchase order cancelled: %s", order_id)
            
        else:
            logger.warning("Failed to cancel purchase order %s: %s", order_id, result.error)

        return result

    def confirm_purchase_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Confirm a draft purchase order."""
        result = self.purchases.confirm_purchase_order(order_id, data)
        if result.ok:
            logger.debug("Purchase order confirmed: %s", order_id)
        else:
            logger.warning("Failed to confirm purchase order %s: %s", order_id, result.error)
        return result

    def complete_purchase_order(self, order_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Complete a purchase order."""
        result = self.purchases.complete_purchase_order(order_id, data)
        if result.ok:
            logger.debug("Purchase order completed: %s", order_id)
        else:
            logger.warning("Failed to complete purchase order %s: %s", order_id, result.error)
        return result

    # ------------------------------------------------------------------
    # Purchase Invoices
    # ------------------------------------------------------------------
    def load_purchase_invoices(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal[
            tuple(code for code, _ in INVOICE_STATUS)
        ] | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
        supplier: int | None = None,
        order: int | None = None,
    ) -> APIResult:
        """
        Fetch the purchase invoice list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.
        """
        result = self.purchases.list_purchase_invoices(
            page=page,
            page_size=page_size,
            search=search,
            supplier=supplier,
            order=order,
            status=status,
            is_active=is_active or None,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Purchase invoices loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )

        else:
            logger.warning("Failed to load purchase invoices: %s", result.error)

        return result

    def create_purchase_invoice(self, invoice_data: dict[str, Any]) -> APIResult:
        """Create a new purchase invoice."""
        result = self.purchases.create_purchase_invoice(invoice_data)

        if result.ok:
            logger.debug("Purchase invoice created: %s", result.data.get("id"))

        else:
            logger.warning("Failed to create purchase invoice: %s", result.error)

        return result

    def get_purchase_invoice(self, invoice_id: int) -> APIResult:
        """Retrieve a specific purchase invoice."""
        result = self.purchases.get_purchase_invoice(invoice_id)

        if result.ok:
            logger.debug("Purchase invoice loaded: %s", invoice_id)

        else:
            logger.warning("Failed to load purchase invoice %s: %s", invoice_id, result.error)

        return result

    def update_purchase_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """Fully update a purchase invoice."""
        result = self.purchases.update_purchase_invoice(invoice_id, invoice_data)

        if result.ok:
            logger.debug("Purchase invoice updated: %s", invoice_id)

        else:
            logger.warning("Failed to update purchase invoice %s: %s", invoice_id, result.error)

        return result

    def partial_update_purchase_invoice(self, invoice_id: int, invoice_data: dict[str, Any]) -> APIResult:
        """Partially update a purchase invoice."""
        result = self.purchases.partial_update_purchase_invoice(invoice_id, invoice_data)

        if result.ok:
            logger.debug("Purchase invoice partially updated: %s", invoice_id)

        else:
            logger.warning(
                "Failed to partially update purchase invoice %s: %s", invoice_id, result.error
            )

        return result

    def delete_purchase_invoice(self, invoice_id: int) -> APIResult:
        """Delete a purchase invoice."""
        result = self.purchases.delete_purchase_invoice(invoice_id)

        if result.ok:
            logger.debug("Purchase invoice deleted: %s", invoice_id)

        else:
            logger.warning("Failed to delete purchase invoice %s: %s", invoice_id, result.error)

        return result

    def post_purchase_invoice(self, invoice_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Post a purchase invoice (idempotent; stock received on create)."""
        result = self.purchases.post_purchase_invoice(invoice_id, data)

        if result.ok:
            logger.debug("Purchase invoice posted: %s", invoice_id)

        else:
            logger.warning("Failed to post purchase invoice %s: %s", invoice_id, result.error)

        return result

    def cancel_purchase_invoice(self, invoice_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Cancel a purchase invoice (reverses received stock if unpaid)."""
        result = self.purchases.cancel_purchase_invoice(invoice_id, data)
        if result.ok:
            logger.debug("Purchase invoice cancelled: %s", invoice_id)
        else:
            logger.warning("Failed to cancel purchase invoice %s: %s", invoice_id, result.error)
        return result

    # ------------------------------------------------------------------
    # Purchase Payments
    # ------------------------------------------------------------------

    def load_purchase_payments(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        status: Literal[
            "completed", "failed", "partial", "pending", "refunded"
        ] | None = None,
        ordering: str | None = None,
        supplier: int | None = None,
        order: int | None = None,
        invoice: int | None = None,
    ) -> APIResult:
        """
        Fetch the purchase payment list and return the raw APIResult so the
        widget/view decides how to render success, empty, and error states.

        Parameter order matches the Payments tab call:
        page, page_size, search, status.
        """
        result = self.purchases.list_purchase_payments(
            page=page,
            page_size=page_size,
            search=search,
            supplier=supplier,
            order=order,
            invoice=invoice,
            status=status,
            ordering=ordering,
        )

        if result.ok:
            logger.debug(
                "Purchase payments loaded: %d / %d",
                len(result.data.get("results", [])),
                result.data.get("count", 0),
            )
        else:
            logger.warning("Failed to load purchase payments: %s", result.error)

        return result

    def create_purchase_payment(self, payment_data: dict[str, Any]) -> APIResult:
        """Create a new purchase payment."""
        result = self.purchases.create_purchase_payment(payment_data)

        if result.ok:
            logger.debug("Purchase payment created: %s", result.data.get("id"))
            
        else:
            logger.warning("Failed to create purchase payment: %s", result.error)

        return result

    def get_purchase_payment(self, payment_id: int) -> APIResult:
        """Retrieve a specific purchase payment."""
        result = self.purchases.get_purchase_payment(payment_id)

        if result.ok:
            logger.debug("Purchase payment loaded: %s", payment_id)

        else:
            logger.warning("Failed to load purchase payment %s: %s", payment_id, result.error)

        return result

    def update_purchase_payment(self, payment_id: int, payment_data: dict[str, Any]) -> APIResult:
        """Fully update a purchase payment."""
        result = self.purchases.update_purchase_payment(payment_id, payment_data)

        if result.ok:
            logger.debug("Purchase payment updated: %s", payment_id)

        else:
            logger.warning("Failed to update purchase payment %s: %s", payment_id, result.error)

        return result

    def partial_update_purchase_payment(self, payment_id: int, payment_data: dict[str, Any]) -> APIResult:
        """Partially update a purchase payment."""
        result = self.purchases.partial_update_purchase_payment(payment_id, payment_data)

        if result.ok:
            logger.debug("Purchase payment partially updated: %s", payment_id)

        else:
            logger.warning(
                "Failed to partially update purchase payment %s: %s", payment_id, result.error
            )

        return result

    def delete_purchase_payment(self, payment_id: int) -> APIResult:
        """Delete a purchase payment."""
        result = self.purchases.delete_purchase_payment(payment_id)

        if result.ok:
            logger.debug("Purchase payment deleted: %s", payment_id)

        else:
            logger.warning("Failed to delete purchase payment %s: %s", payment_id, result.error)

        return result

    def refund_purchase_payment(self, payment_id: int, data: dict[str, Any] | None = None) -> APIResult:
        """Refund a purchase payment and adjust invoice balance."""
        result = self.purchases.refund_purchase_payment(payment_id, data)
        if result.ok:
            logger.debug("Purchase payment refunded: %s", payment_id)
        else:
            logger.warning("Failed to refund purchase payment %s: %s", payment_id, result.error)
        return result
