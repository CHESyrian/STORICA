from django.db import transaction

from common.generators import GenCodeEngine
from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
    ConflictException,
)
from common.models.choices import (
    OrderStatus,
    PaymentStatus,
    InvoiceStatus,
)

from apps.purchases.models import (
    PurchasesOrder,
    PurchasesPayment,
    PurchasesInvoice,
)


# =========================================================
# PURCHASES PAYMENT SERVICE
# =========================================================
class PurchasesPaymentService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(payment_id: int) -> PurchasesPayment:
        try:
            return (
                PurchasesPayment.objects
                .select_related(
                    "invoice", "order", "supplier", "processed_by"
                )
                .get(pk=payment_id)
            )
        except PurchasesPayment.DoesNotExist:
            raise NotFoundException(
                message=f"Payment with id {payment_id} not found."
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(
        validated_data: dict,
        user=None,
        adjust_invoice_balance: bool = True,
    ) -> PurchasesPayment:
        """
        Create a payment against an invoice.

        By default validates amount against remaining balance and
        increments ``invoice.amount_paid``.

        Pass ``adjust_invoice_balance=False`` when the caller already
        set ``invoice.amount_paid`` (e.g. invoice create).

        Order is optional: falls back to ``invoice.order`` so standalone
        invoices (no PO) can accept payments.
        """
        # of=("self",): order is a nullable FK; Postgres rejects
        # FOR UPDATE on the nullable side of an outer join.
        invoice: PurchasesInvoice = (
            PurchasesInvoice.objects
            .select_for_update(of=("self",))
            .get(pk=validated_data["invoice"].pk)
        )

        order = validated_data.get("order") or invoice.order
        locked_order = None
        if order is not None:
            locked_order = (
                PurchasesOrder.objects
                .select_for_update(of=("self",))
                .get(pk=order.pk)
            )

        transaction_id = GenCodeEngine.transaction("TNX")
        if transaction_id and PurchasesPayment.objects.filter(
            transaction_id=transaction_id
        ).exists():
            raise ConflictException(
                message=(
                    "A payment with this transaction ID already exists."
                )
            )

        status = validated_data.get("status")

        if adjust_invoice_balance:
            remaining = invoice.total_amount - invoice.amount_paid

            if validated_data["amount"] > remaining:
                raise BusinessLogicException(
                    message=(
                        f"Payment amount exceeds remaining balance "
                        f"({remaining})."
                    )
                )

            if validated_data["amount"] == remaining:
                status = PaymentStatus.COMPLETED.value
            else:
                status = PaymentStatus.PARTIAL.value

        # Never persist null status.
        if not status:
            status = PaymentStatus.COMPLETED.value

        payment_kwargs = {
            "transaction_id": transaction_id,
            "invoice": invoice,
            "order": locked_order,
            "supplier": validated_data["supplier"],
            "amount": validated_data["amount"],
            "reference_number": transaction_id,
            "notes": validated_data.get("notes", ""),
            "processed_by": user or validated_data.get("processed_by"),
            "status": status,
        }
        if validated_data.get("payment_date") is not None:
            payment_kwargs["payment_date"] = validated_data[
                "payment_date"
            ]
        payment = PurchasesPayment.objects.create(**payment_kwargs)

        if adjust_invoice_balance:
            invoice.amount_paid += validated_data["amount"]

            if status == PaymentStatus.COMPLETED.value:
                invoice.status = InvoiceStatus.PAID.value
                if locked_order is not None:
                    locked_order.status = OrderStatus.COMPLETED.value
                    locked_order.save()
            elif status == PaymentStatus.PARTIAL.value:
                invoice.status = InvoiceStatus.PARTIAL.value

            invoice.save()

        from apps.accounting.services.event_service import LedgerEventService

        if status in {
            PaymentStatus.COMPLETED.value,
            PaymentStatus.PARTIAL.value,
        }:
            LedgerEventService.on_purchase_payment_completed(
                payment, user=user
            )

        return payment

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        payment_id: int,
        validated_data: dict,
        partial: bool = False,
        user=None,
    ) -> PurchasesPayment:
        payment = PurchasesPayment.objects.select_for_update().get(
            pk=payment_id
        )

        if (
            payment.status == PaymentStatus.COMPLETED.value
            and validated_data.get("status")
            not in {None, PaymentStatus.REFUNDED.value}
        ):
            raise BusinessLogicException(
                message=(
                    "A completed payment can only be set to refunded."
                )
            )

        fields = ["status", "reference_number", "notes"]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(payment, field, validated_data[field])

        payment.save()
        return payment

    # --------------------------------------------------
    # REFUND
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def refund(payment_id: int, user=None) -> PurchasesPayment:
        """
        Mark a completed/partial payment as refunded and reduce the
        invoice amount_paid (and status) accordingly.
        """
        payment = (
            PurchasesPayment.objects
            .select_for_update(of=("self",))
            .get(pk=payment_id)
        )

        if payment.status == PaymentStatus.REFUNDED.value:
            raise BusinessLogicException(
                message="Payment is already refunded."
            )

        if payment.status not in {
            PaymentStatus.COMPLETED.value,
            PaymentStatus.PARTIAL.value,
        }:
            raise BusinessLogicException(
                message=(
                    f"Cannot refund a payment with status "
                    f"'{payment.status}'."
                )
            )

        invoice = (
            PurchasesInvoice.objects
            .select_for_update()
            .get(pk=payment.invoice_id)
        )

        invoice.amount_paid -= payment.amount
        if invoice.amount_paid < 0:
            invoice.amount_paid = 0

        if invoice.amount_paid == 0:
            invoice.status = InvoiceStatus.SENT.value
            invoice.paid_date = None
        elif invoice.amount_paid < invoice.total_amount:
            invoice.status = InvoiceStatus.PARTIAL.value
            invoice.paid_date = None
        invoice.save()

        payment.status = PaymentStatus.REFUNDED.value
        payment.save()

        from apps.accounting.services.event_service import LedgerEventService

        LedgerEventService.on_purchase_payment_refunded(
            payment, user=user
        )

        return payment

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(payment_id: int) -> None:
        payment = PurchasesPayment.objects.select_for_update().get(
            pk=payment_id
        )

        if payment.status in {
            PaymentStatus.COMPLETED.value,
            PaymentStatus.PARTIAL.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Cannot delete a completed or partial payment. "
                    "Use refund instead."
                )
            )

        if payment.status != PaymentStatus.REFUNDED.value:
            invoice = PurchasesInvoice.objects.select_for_update().get(
                pk=payment.invoice.pk
            )
            invoice.amount_paid -= payment.amount
            if invoice.amount_paid < 0:
                invoice.amount_paid = 0
            invoice.save()

        payment.delete()
