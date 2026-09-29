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
    StockMovementType,
    MovementStatus,
)

from apps.inventory.services.batch_service import BatchService
from apps.inventory.services.stock_movement_service import (
    StockMovementService,
)
from apps.sales.models import SalesInvoice, SalesInvoiceItem, SalesOrder


# =========================================================
# SALES INVOICE SERVICE
# =========================================================
class SalesInvoiceService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(invoice_id: int) -> SalesInvoice:
        try:
            return (
                SalesInvoice.objects
                .select_related("customer", "order")
                .prefetch_related("items__variant")
                .get(pk=invoice_id)
            )
        except SalesInvoice.DoesNotExist:
            raise NotFoundException(
                message=f"Invoice with id {invoice_id} not found."
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user=None) -> SalesInvoice:
        items_data = validated_data.pop("items")

        order = validated_data.get("order")
        if order and SalesInvoice.objects.filter(
            order=order
        ).exists():
            raise ConflictException(
                message="An invoice for this order already exists."
            )

        # Always derive total from line items (ignore client total
        # when lines are present) so header and lines stay consistent.
        computed_total = SalesInvoiceService._compute_total(
            items_data
        )
        client_total = validated_data.get("total_amount")
        if client_total is not None and client_total != computed_total:
            # Prefer computed; tolerate clients that still send totals.
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

        invoice_kwargs = {
            "customer": validated_data["customer"],
            "order": order,
            "discount_rate": validated_data.get("discount_rate", 0),
            "tax_rate": validated_data.get("tax_rate", 10),
            "total_amount": total_amount,
            "amount_paid": validated_data.get("amount_paid", 0),
            "notes": validated_data.get("notes", ""),
        }
        if validated_data.get("invoice_date") is not None:
            invoice_kwargs["invoice_date"] = validated_data["invoice_date"]
        invoice = SalesInvoice(**invoice_kwargs)

        invoice.code = GenCodeEngine.salas_invoice(SalesInvoice)

        if user:
            invoice.created_by = user
            invoice.updated_by = user

        invoice.save()

        SalesInvoiceService._create_items(invoice, items_data)

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
    ) -> SalesInvoice:
        invoice = SalesInvoice.objects.select_for_update().get(
            pk=invoice_id
        )

        if invoice.status == InvoiceStatus.CANCELLED.value:
            raise BusinessLogicException(
                message="Cannot update a cancelled invoice."
            )

        if invoice.status not in {
            InvoiceStatus.DRAFT.value,
            InvoiceStatus.SENT.value,
        }:
            raise BusinessLogicException(
                message=(
                    f"Cannot update an invoice with status "
                    f"'{invoice.status}'."
                )
            )

        fields = [
            "customer",
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
    # POST INVOICE (change status + stock out via FIFO)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def post_invoice(
        invoice_id: int, user=None
    ) -> SalesInvoice:
        """
        Post a draft sales invoice: allocate stock FIFO per line,
        create COMPLETED OUT movements, and advance invoice (and order)
        status. Already-posted (SENT/PARTIAL/PAID) invoices cannot be
        posted again.

        Runs under ``@transaction.atomic``. ``BatchService.allocate_fifo``
        is invoked inside this transaction so FIFO batch rows stay
        locked until OUT movements are completed.
        """
        invoice = (
            SalesInvoice.objects
            .select_for_update(of=("self",))
            .select_related("order", "customer")
            .prefetch_related("items__variant__product")
            .get(pk=invoice_id)
        )

        if invoice.status != InvoiceStatus.DRAFT.value:
            raise BusinessLogicException(
                message=(
                    f"Cannot post an invoice with status "
                    f"'{invoice.status}'. Only draft "
                    f"invoices can be posted."
                )
            )

        items = list(invoice.items.all())
        if not items:
            raise BusinessLogicException(
                message="Cannot post an invoice with no line items."
            )

        for item in items:
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
                        "unit_price": item.sale_price,
                        "batch": batch,
                        "from_warehouse": batch.warehouse,
                        "reference_number": invoice.code,
                        "notes": (
                            f"Stock out for sales invoice "
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

        # Advance status: keep PAID/PARTIAL if already paid; else SENT
        if invoice.amount_paid >= invoice.total_amount:
            invoice.status = InvoiceStatus.PAID.value
            if not invoice.paid_date:
                invoice.paid_date = timezone.now().date()
        elif invoice.amount_paid > 0:
            invoice.status = InvoiceStatus.PARTIAL.value
        else:
            invoice.status = InvoiceStatus.SENT.value

        if user:
            invoice.updated_by = user
        invoice.save()

        # Linked order → processing (if still draft/confirmed)
        if invoice.order_id:
            order = SalesOrder.objects.select_for_update().get(
                pk=invoice.order_id
            )
            if order.status in {
                OrderStatus.DRAFT.value,
                OrderStatus.CONFIRMED.value,
            }:
                order.status = OrderStatus.PROCESSING.value
                if user:
                    order.updated_by = user
                order.save()

        from apps.accounting.services.event_service import LedgerEventService

        LedgerEventService.on_sales_invoice_posted(invoice, user=user)

        return invoice

    # --------------------------------------------------
    # CANCEL
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def cancel(invoice_id: int, user=None) -> SalesInvoice:
        """
        Cancel a sales invoice.

        - DRAFT: cancel with no stock impact.
        - SENT with amount_paid == 0: cancel and reverse stock via
          completed RETURN movements (one per original OUT line qty).
        - PARTIAL / PAID / REFUNDED / already CANCELLED: refused.
        """
        invoice = (
            SalesInvoice.objects
            .select_for_update(of=("self",))
            .select_related("order", "customer")
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
                    "Remove or refund payments first."
                )
            )

        was_posted = invoice.status == InvoiceStatus.SENT.value

        if was_posted:
            SalesInvoiceService._reverse_posted_stock(
                invoice, user=user
            )

        invoice.status = InvoiceStatus.CANCELLED.value
        if user:
            invoice.updated_by = user
        invoice.save()

        if was_posted:
            from apps.accounting.services.event_service import (
                LedgerEventService,
            )

            LedgerEventService.on_sales_invoice_cancelled(
                invoice, user=user
            )

        return invoice

    # --------------------------------------------------
    # DELETE (soft)
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(invoice_id: int, user=None) -> None:
        invoice = SalesInvoice.objects.select_for_update().get(
            pk=invoice_id
        )

        if invoice.status not in {
            InvoiceStatus.DRAFT.value,
            InvoiceStatus.CANCELLED.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Only draft or cancelled invoices "
                    "can be deleted."
                )
            )

        invoice.soft_delete(deleted_by=user)

    # --------------------------------------------------
    # INTERNAL HELPERS
    # --------------------------------------------------
    @staticmethod
    def _compute_total(items_data: list) -> Decimal:
        """
        Line total = qty * price * (1 - disc/100) * (1 + tax/100).
        Summed across all lines, quantized to 2 decimal places.
        """
        total = Decimal("0")
        for item in items_data:
            qty = Decimal(str(item["quantity"]))
            price = Decimal(str(item["sale_price"]))
            disc = Decimal(str(item.get("discount_rate", 0) or 0))
            tax = Decimal(str(item.get("tax_rate", 0) or 0))
            line = qty * price
            line = line * (Decimal("1") - disc / Decimal("100"))
            line = line * (Decimal("1") + tax / Decimal("100"))
            total += line
        return total.quantize(Decimal("0.01"))

    @staticmethod
    def _create_items(
        invoice: SalesInvoice,
        items_data: list,
    ) -> None:
        items = [
            SalesInvoiceItem(
                invoice=invoice,
                variant=item["variant"],
                quantity=item["quantity"],
                sale_price=item["sale_price"],
                discount_rate=item.get("discount_rate", 0),
                tax_rate=item.get("tax_rate", 0),
                notes=item.get("notes", ""),
            )
            for item in items_data
        ]
        SalesInvoiceItem.objects.bulk_create(items)

    @staticmethod
    def _reverse_posted_stock(invoice: SalesInvoice, user=None) -> None:
        """
        Reverse stock deducted by post_invoice: create completed RETURN
        movements for each invoice line, allocating into existing batches
        when possible (FIFO preference via first active batch).
        """
        from apps.inventory.models import Batch
        from common.models.choices import BatchStatus

        for item in invoice.items.all():
            remaining = item.quantity
            batches = list(
                Batch.objects
                .select_for_update()
                .filter(
                    variant=item.variant,
                    status=BatchStatus.ACTIVE,
                    is_active=True,
                )
                .order_by("production_date", "id")
            )
            if not batches:
                raise BusinessLogicException(
                    message=(
                        f"Cannot reverse stock for variant "
                        f"'{item.variant}': no active batch found."
                    )
                )

            # Put the full quantity back on the earliest batch.
            batch = batches[0]
            movement = StockMovementService.create(
                {
                    "movement_type": StockMovementType.RETURN,
                    "product": item.variant.product,
                    "quantity": remaining,
                    "unit_price": item.sale_price,
                    "batch": batch,
                    "to_warehouse": batch.warehouse,
                    "reference_number": invoice.code,
                    "notes": (
                        f"Stock return for cancelled sales invoice "
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
