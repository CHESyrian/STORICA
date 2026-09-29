from django.db import transaction

from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
    ConflictException,
)
from common.models.choices import PaymentStatus

from apps.sales.models import SalesPayment, SalesInvoice


# =========================================================
# SALES PAYMENT SERVICE
# =========================================================
class SalesPaymentService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(payment_id: int) -> SalesPayment:
        try:
            return (
                SalesPayment.objects
                .select_related(
                    "invoice",
                    "order",
                    "customer",
                    "processed_by",
                )
                .get(pk=payment_id)
            )
        except SalesPayment.DoesNotExist:
            raise NotFoundException(
                message=(
                    f"Payment with id {payment_id} not found."
                )
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(
        validated_data: dict, user=None
    ) -> SalesPayment:
        invoice: SalesInvoice = (
            SalesInvoice.objects
            .select_for_update(of=("self",))
            .get(pk=validated_data["invoice"].pk)
        )

        transaction_id = validated_data.get("transaction_id", "")
        if transaction_id and SalesPayment.objects.filter(
            transaction_id=transaction_id
        ).exists():
            raise ConflictException(
                message=(
                    "A payment with this transaction ID "
                    "already exists."
                )
            )

        remaining = invoice.total_amount - invoice.amount_paid
        if validated_data["amount"] > remaining:
            raise BusinessLogicException(
                message=(
                    f"Payment amount exceeds remaining "
                    f"balance ({remaining})."
                )
            )

        # Payments are applied immediately when recorded.
        payment_kwargs = {
            "transaction_id": transaction_id,
            "invoice": invoice,
            "order": validated_data.get("order"),
            "customer": validated_data["customer"],
            "amount": validated_data["amount"],
            "reference_number": validated_data.get(
                "reference_number", ""
            ),
            "notes": validated_data.get("notes", ""),
            "processed_by": validated_data["processed_by"],
            "status": PaymentStatus.COMPLETED.value,
        }
        if validated_data.get("payment_date") is not None:
            payment_kwargs["payment_date"] = validated_data["payment_date"]
        payment = SalesPayment.objects.create(**payment_kwargs)

        invoice.amount_paid += validated_data["amount"]
        invoice.save()

        from apps.accounting.services.event_service import LedgerEventService

        LedgerEventService.on_sales_payment_completed(payment, user=user)

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
    ) -> SalesPayment:
        payment = SalesPayment.objects.select_for_update().get(
            pk=payment_id
        )

        if (
            payment.status == PaymentStatus.COMPLETED.value
            and validated_data.get("status")
            not in {None, PaymentStatus.REFUNDED.value}
        ):
            raise BusinessLogicException(
                message=(
                    "A completed payment can only be "
                    "set to refunded."
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
    def refund(payment_id: int, user=None) -> SalesPayment:
        """
        Mark a completed/partial payment as refunded and reduce the
        invoice amount_paid. Invoice status is recalculated on save
        (PAID / PARTIAL / unpaid). Does not reverse stock.
        """
        payment = (
            SalesPayment.objects
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
            SalesInvoice.objects
            .select_for_update(of=("self",))
            .get(pk=payment.invoice_id)
        )

        invoice.amount_paid -= payment.amount
        if invoice.amount_paid < 0:
            invoice.amount_paid = 0
        # Model.save() sets PAID / PARTIAL from amount_paid.
        # When fully unpaid, force back to SENT if it was posted,
        # else leave DRAFT.
        if invoice.amount_paid == 0:
            from common.models.choices import InvoiceStatus

            if invoice.status in {
                InvoiceStatus.PAID.value,
                InvoiceStatus.PARTIAL.value,
                InvoiceStatus.OVERDUE.value,
            }:
                invoice.status = InvoiceStatus.SENT.value
                invoice.paid_date = None
            # Avoid save() re-promoting to PARTIAL/PAID with 0 paid:
            # save() only upgrades when amount_paid > 0 / full.
        invoice.save()

        payment.status = PaymentStatus.REFUNDED.value
        payment.save()

        from apps.accounting.services.event_service import LedgerEventService

        LedgerEventService.on_sales_payment_refunded(payment, user=user)

        return payment

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(payment_id: int) -> None:
        payment = SalesPayment.objects.select_for_update(
            of=("self",)
        ).get(pk=payment_id)

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
            invoice = SalesInvoice.objects.select_for_update(
                of=("self",)
            ).get(pk=payment.invoice.pk)
            invoice.amount_paid -= payment.amount
            if invoice.amount_paid < 0:
                invoice.amount_paid = 0
            invoice.save()

        payment.delete()
