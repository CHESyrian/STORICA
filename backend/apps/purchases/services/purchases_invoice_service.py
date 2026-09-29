from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from common.generators import GenCodeEngine
from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
    ConflictException,
)
from common.models.choices import (
    InvoiceStatus,
    OrderStatus,
    PaymentStatus,
    BatchStatus,
    StockMovementType,
    MovementStatus,
)

from apps.purchases.models import (
    PurchasesInvoice,
    PurchasesInvoiceItem,
    PurchasesOrder,
)

from apps.purchases.services.purchases_payment_service import (
    PurchasesPaymentService,
)

from apps.inventory.models import StockMovement
from apps.inventory.services.batch_service import BatchService
from apps.inventory.services.stock_movement_service import (
    StockMovementService,
)


# =========================================================
# PURCHASES INVOICE SERVICE
# =========================================================
class PurchasesInvoiceService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(invoice_id: int) -> PurchasesInvoice:
        try:
            return (
                PurchasesInvoice.objects
                .select_related("supplier", "order", "warehouse")
                .prefetch_related("items__variant")
                .get(pk=invoice_id)
            )
        except PurchasesInvoice.DoesNotExist:
            raise NotFoundException(
                message=f"Invoice with id {invoice_id} not found."
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user=None) -> PurchasesInvoice:
        items_data = validated_data.pop("items")
        warehouse = validated_data.get("warehouse")
        if warehouse is None:
            raise BusinessLogicException(
                message="Warehouse is required to receive purchase stock."
            )

        order = validated_data.get("order")
        if order and PurchasesInvoice.objects.filter(
            order=order
        ).exists():
            raise ConflictException(
                message="An invoice for this order already exists."
            )

        # Prefer line-computed total so header and items stay aligned.
        computed_total = PurchasesInvoiceService._compute_total(
            items_data
        )
        client_total = validated_data.get("total_amount")
        if client_total is not None and client_total != computed_total:
            total_amount = computed_total
        else:
            total_amount = (
                computed_total
                if computed_total > 0
                else validated_data.get("total_amount", Decimal("0"))
            )

        if total_amount <= 0:
            raise BusinessLogicException(
                message="Invoice total must be greater than 0."
            )

        amount_paid = validated_data.get("amount_paid", 0) or 0

        status = PurchasesInvoiceService._resolve_status(
            amount_paid=amount_paid, total_amount=total_amount
        )

        invoice_kwargs = {
            "supplier": validated_data["supplier"],
            "order": order,
            "warehouse": warehouse,
            "discount_rate": validated_data.get("discount_rate", 0),
            "tax_rate": validated_data.get("tax_rate", 0),
            "total_amount": total_amount,
            "amount_paid": amount_paid,
            "status": status,
            "notes": validated_data.get("notes", ""),
        }
        if validated_data.get("invoice_date") is not None:
            invoice_kwargs["invoice_date"] = validated_data["invoice_date"]
        invoice = PurchasesInvoice(**invoice_kwargs)

        invoice.code = GenCodeEngine.purchase_invoice(
            PurchasesInvoice
        )

        if user:
            invoice.created_by = user
            invoice.updated_by = user

        invoice.save()

        PurchasesInvoiceService._create_items(invoice, items_data)

        PurchasesInvoiceService._receive_stock(invoice, user=user)

        from apps.accounting.services.event_service import LedgerEventService

        LedgerEventService.on_purchase_invoice_received(invoice, user=user)

        if amount_paid > 0:
            payment_status = (
                PaymentStatus.COMPLETED.value
                if status == InvoiceStatus.PAID.value
                else PaymentStatus.PARTIAL.value
            )
            PurchasesInvoiceService._create_payment(
                invoice=invoice,
                amount=amount_paid,
                status=payment_status,
                user=user,
            )

        if order:
            new_order_status = (
                OrderStatus.COMPLETED.value
                if status == InvoiceStatus.PAID.value
                else OrderStatus.PROCESSING.value
            )
            PurchasesInvoiceService._set_order_status(
                order=order, status=new_order_status, user=user
            )

        return invoice

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        invoice_id: int,
        validated_data: dict,
        user=None,
        partial: bool = False,
    ) -> PurchasesInvoice:
        invoice = PurchasesInvoice.objects.select_for_update().get(
            pk=invoice_id
        )

        if invoice.status == InvoiceStatus.CANCELLED.value:
            raise BusinessLogicException(
                message="Cannot update a cancelled invoice."
            )

        # After receive-on-create, only notes (and limited header fields)
        # should change. Block amount / counterparty edits on non-draft.
        if invoice.status not in {
            InvoiceStatus.DRAFT.value,
        }:
            blocked = {
                "supplier",
                "order",
                "warehouse",
                "total_amount",
                "amount_paid",
                "discount_rate",
                "tax_rate",
            }
            attempted = blocked.intersection(validated_data.keys())
            if attempted:
                raise BusinessLogicException(
                    message=(
                        "Cannot change "
                        f"{', '.join(sorted(attempted))} on an "
                        f"invoice with status '{invoice.status}'. "
                        "Cancel and re-create if needed."
                    )
                )

        fields = [
            "supplier",
            "order",
            "invoice_date",
            "discount_rate",
            "tax_rate",
            "total_amount",
            "amount_paid",
            "notes",
        ]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(invoice, field, validated_data[field])

        if user:
            invoice.updated_by = user

        invoice.save()
        return invoice

    # --------------------------------------------------
    # POST INVOICE (idempotent — stock already on create)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def post_invoice(
        invoice_id: int, user=None
    ) -> "PurchasesInvoice":
        """
        Purchase invoices receive stock on create. This endpoint is
        kept for API symmetry with sales and is a no-op success when
        the invoice is already received (not cancelled).
        """
        invoice = (
            PurchasesInvoice.objects
            .select_for_update(of=("self",))
            .select_related("supplier", "order", "warehouse")
            .prefetch_related("items")
            .get(pk=invoice_id)
        )

        if invoice.status == InvoiceStatus.CANCELLED.value:
            raise BusinessLogicException(
                message="Cannot post a cancelled purchase invoice."
            )

        if user:
            invoice.updated_by = user
            invoice.save()
        return invoice

    # --------------------------------------------------
    # CANCEL
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def cancel(invoice_id: int, user=None) -> PurchasesInvoice:
        """
        Cancel a purchase invoice.

        - Unpaid SENT (or residual DRAFT): reverse received stock via
          completed OUT movements against the original receipt batches,
          then mark CANCELLED.
        - PARTIAL / PAID / REFUNDED / already CANCELLED: refused.
        """
        invoice = (
            PurchasesInvoice.objects
            .select_for_update(of=("self",))
            .select_related("supplier", "order", "warehouse")
            .prefetch_related("items__variant__product")
            .get(pk=invoice_id)
        )

        if invoice.status == InvoiceStatus.CANCELLED.value:
            raise BusinessLogicException(
                message="Invoice is already cancelled."
            )

        if invoice.status in {
            InvoiceStatus.PAID.value,
            InvoiceStatus.PARTIAL.value,
            InvoiceStatus.REFUNDED.value,
            InvoiceStatus.OVERDUE.value,
        }:
            raise BusinessLogicException(
                message=(
                    f"Cannot cancel an invoice with status "
                    f"'{invoice.status}'. Refund or settle "
                    f"payments first."
                )
            )

        if invoice.amount_paid and invoice.amount_paid > 0:
            raise BusinessLogicException(
                message=(
                    "Cannot cancel an invoice that has payments. "
                    "Refund payments first."
                )
            )

        # Reverse stock received on create (reference = invoice code).
        PurchasesInvoiceService._reverse_received_stock(
            invoice, user=user
        )

        invoice.status = InvoiceStatus.CANCELLED.value
        if user:
            invoice.updated_by = user
        invoice.save()

        from apps.accounting.services.event_service import LedgerEventService

        LedgerEventService.on_purchase_invoice_cancelled(
            invoice, user=user
        )

        return invoice

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(invoice_id: int, user=None) -> None:
        invoice = PurchasesInvoice.objects.select_for_update().get(
            pk=invoice_id
        )

        if invoice.status not in {
            InvoiceStatus.DRAFT.value,
            InvoiceStatus.CANCELLED.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Only draft or cancelled invoices can be deleted."
                )
            )

        invoice.soft_delete(deleted_by=user)

    # --------------------------------------------------
    # INTERNAL HELPERS
    # --------------------------------------------------
    @staticmethod
    def _compute_total(items_data: list) -> Decimal:
        """
        Line total = qty * cost * (1 - disc/100) * (1 + tax/100).
        """
        total = Decimal("0")
        for item in items_data:
            qty = Decimal(str(item["quantity"]))
            price = Decimal(str(item["cost_price"]))
            disc = Decimal(str(item.get("discount_rate", 0) or 0))
            tax = Decimal(str(item.get("tax_rate", 0) or 0))
            line = qty * price
            line = line * (Decimal("1") - disc / Decimal("100"))
            line = line * (Decimal("1") + tax / Decimal("100"))
            total += line
        return total.quantize(Decimal("0.01"))

    @staticmethod
    def _create_items(
        invoice: PurchasesInvoice,
        items_data: list,
    ) -> None:
        items = [
            PurchasesInvoiceItem(
                invoice=invoice,
                variant=item["variant"],
                quantity=item["quantity"],
                cost_price=item["cost_price"],
                discount_rate=item.get("discount_rate", 0),
                tax_rate=item.get("tax_rate", 0),
                notes=item.get("notes", ""),
                production_date=item["production_date"],
                expiry_date=item.get("expiry_date"),
            )
            for item in items_data
        ]
        PurchasesInvoiceItem.objects.bulk_create(items)

    @staticmethod
    def _resolve_status(amount_paid, total_amount) -> str:
        """Map the amount paid at creation time to an invoice status."""
        amount_paid = amount_paid or 0
        if amount_paid < 0:
            raise BusinessLogicException(
                message="Amount paid cannot be negative."
            )

        if amount_paid > total_amount:
            raise BusinessLogicException(
                message="Amount paid cannot exceed total amount."
            )

        if amount_paid == 0:
            return InvoiceStatus.SENT.value

        if amount_paid == total_amount:
            return InvoiceStatus.PAID.value

        return InvoiceStatus.PARTIAL.value

    @staticmethod
    def _receive_stock(invoice: PurchasesInvoice, user=None) -> None:
        """
        For every invoice item: create a batch via BatchService
        (bumps variant.quantity), then log a matching stock-in
        movement via the receipt-only path (no double count).
        """
        warehouse = invoice.warehouse

        for item in invoice.items.select_related("variant__product"):
            batch = BatchService.create(
                {
                    "variant": item.variant,
                    "warehouse": warehouse,
                    "quantity": item.quantity,
                    "cost_price": item.cost_price,
                    "production_date": item.production_date,
                    "expiry_date": item.expiry_date,
                    "status": BatchStatus.ACTIVE,
                },
                user=user,
            )

            StockMovementService.record_purchase_receipt(
                {
                    "movement_type": StockMovementType.IN,
                    "product": item.variant.product,
                    "quantity": item.quantity,
                    "unit_price": item.cost_price,
                    "batch": batch,
                    "to_warehouse": warehouse,
                    "reference_number": invoice.code,
                    "performed_by": user,
                    "created_by": user,
                    "notes": (
                        f"Stock in from purchase invoice {invoice.code}"
                    ),
                },
                user=user,
            )

    @staticmethod
    def _reverse_received_stock(
        invoice: PurchasesInvoice, user=None
    ) -> None:
        """
        Reverse stock from create: for each completed IN movement
        tagged with this invoice code, create and complete an OUT
        against the same batch.

        Called only from ``cancel()`` (already ``@transaction.atomic``).
        The FIFO fallback path uses ``BatchService.allocate_fifo``, which
        requires that outer transaction so batch locks are held.
        """
        # of=("self",): batch/from_warehouse/to_warehouse are nullable;
        # Postgres rejects FOR UPDATE on the nullable side of an outer join.
        receipts = list(
            StockMovement.objects
            .select_for_update(of=("self",))
            .select_related("batch", "product")
            .filter(
                reference_number=invoice.code,
                movement_type=StockMovementType.IN,
                status=MovementStatus.COMPLETED,
            )
        )

        if not receipts and invoice.items.exists():
            # Fallback: OUT via FIFO per line if receipt rows missing.
            for item in invoice.items.select_related(
                "variant__product"
            ):
                allocations = BatchService.allocate_fifo(
                    variant=item.variant,
                    quantity=item.quantity,
                )
                for batch, qty in allocations:
                    movement = StockMovementService.create(
                        {
                            "movement_type": StockMovementType.OUT,
                            "product": item.variant.product,
                            "quantity": qty,
                            "unit_price": item.cost_price,
                            "batch": batch,
                            "from_warehouse": batch.warehouse,
                            "reference_number": invoice.code,
                            "notes": (
                                f"Stock out for cancelled purchase "
                                f"invoice {invoice.code}"
                            ),
                            "performed_by": user,
                            "created_by": user,
                            "movement_date": timezone.now(),
                        },
                        user=user,
                    )
                    StockMovementService.update(
                        movement.pk,
                        {"status": MovementStatus.COMPLETED},
                        user=user,
                    )
            return

        for receipt in receipts:
            if not receipt.batch_id:
                raise BusinessLogicException(
                    message=(
                        f"Cannot reverse receipt movement "
                        f"{receipt.pk}: no batch linked."
                    )
                )
            movement = StockMovementService.create(
                {
                    "movement_type": StockMovementType.OUT,
                    "product": receipt.product,
                    "quantity": receipt.quantity,
                    "unit_price": receipt.unit_price,
                    "batch": receipt.batch,
                    "from_warehouse": (
                        receipt.batch.warehouse
                        if receipt.batch_id
                        else invoice.warehouse
                    ),
                    "reference_number": invoice.code,
                    "notes": (
                        f"Stock out for cancelled purchase invoice "
                        f"{invoice.code}"
                    ),
                    "performed_by": user,
                    "created_by": user,
                    "movement_date": timezone.now(),
                },
                user=user,
            )
            StockMovementService.update(
                movement.pk,
                {"status": MovementStatus.COMPLETED},
                user=user,
            )

    @staticmethod
    def _create_payment(
        invoice: PurchasesInvoice,
        amount,
        status: str,
        user=None,
    ) -> None:
        # adjust_invoice_balance=False: amount_paid already set on create.
        PurchasesPaymentService.create(
            {
                "invoice": invoice,
                "order": invoice.order,
                "supplier": invoice.supplier,
                "amount": amount,
                "payment_date": timezone.now(),
                "processed_by": user,
                "status": status,
            },
            user=user,
            adjust_invoice_balance=False,
        )

    @staticmethod
    def _set_order_status(
        order: PurchasesOrder,
        status: str,
        user=None,
    ) -> None:
        locked_order = PurchasesOrder.objects.select_for_update().get(
            pk=order.pk
        )
        locked_order.status = status
        if user:
            locked_order.updated_by = user
        locked_order.save()
