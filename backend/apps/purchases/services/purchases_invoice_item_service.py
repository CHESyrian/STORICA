from django.db import transaction

from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
    ConflictException,
)
from common.models.choices import InvoiceStatus

from apps.purchases.models import PurchasesInvoiceItem


# =========================================================
# PURCHASES INVOICE ITEM SERVICE
# =========================================================
class PurchasesInvoiceItemService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(item_id: int) -> PurchasesInvoiceItem:
        try:
            return (
                PurchasesInvoiceItem.objects
                .select_related("invoice", "variant")
                .get(pk=item_id)
            )
        except PurchasesInvoiceItem.DoesNotExist:
            raise NotFoundException(
                message=f"Invoice item with id {item_id} not found."
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict) -> PurchasesInvoiceItem:
        invoice = validated_data["invoice"]
        variant = validated_data["variant"]

        if invoice.status not in {
            InvoiceStatus.DRAFT.value,
            InvoiceStatus.SENT.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Items can only be added to draft or sent invoices."
                )
            )

        if PurchasesInvoiceItem.objects.filter(
            invoice=invoice, variant=variant
        ).exists():
            raise ConflictException(
                message="This variant already exists in the invoice."
            )

        item = PurchasesInvoiceItem.objects.create(
            invoice=invoice,
            variant=variant,
            quantity=validated_data["quantity"],
            cost_price=validated_data["cost_price"],
            discount_rate=validated_data.get("discount_rate", 0),
            tax_rate=validated_data.get("tax_rate", 0),
            notes=validated_data.get("notes", ""),
        )
        return item

    # --------------------------------------------------
    # UPDATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def update(
        item_id: int,
        validated_data: dict,
        partial: bool = False,
    ) -> PurchasesInvoiceItem:
        item = PurchasesInvoiceItem.objects.select_for_update().get(
            pk=item_id
        )

        if item.invoice.status not in {
            InvoiceStatus.DRAFT.value,
            InvoiceStatus.SENT.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Items can only be updated on draft or "
                    "sent invoices."
                )
            )

        fields = [
            "quantity",
            "cost_price",
            "discount_rate",
            "tax_rate",
            "notes",
        ]

        for field in fields:
            if partial and field not in validated_data:
                continue
            if field in validated_data:
                setattr(item, field, validated_data[field])

        item.save()
        return item

    # --------------------------------------------------
    # DELETE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def delete(item_id: int) -> None:
        item = PurchasesInvoiceItem.objects.select_for_update().get(
            pk=item_id
        )

        if item.invoice.status not in {
            InvoiceStatus.DRAFT.value,
            InvoiceStatus.SENT.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Items can only be removed from draft or "
                    "sent invoices."
                )
            )

        item.delete()
