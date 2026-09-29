from django.db import transaction

from common.exceptions.base import (
    NotFoundException,
    BusinessLogicException,
    ConflictException,
)
from common.models.choices import InvoiceStatus

from apps.sales.models import SalesInvoiceItem


# =========================================================
# SALES INVOICE ITEM SERVICE
# =========================================================
class SalesInvoiceItemService:

    # --------------------------------------------------
    # RETRIEVE
    # --------------------------------------------------
    @staticmethod
    def get_by_id(item_id: int) -> SalesInvoiceItem:
        try:
            return (
                SalesInvoiceItem.objects
                .select_related("invoice__customer", "variant")
                .get(pk=item_id)
            )
        except SalesInvoiceItem.DoesNotExist:
            raise NotFoundException(
                message=(
                    f"Invoice item with id {item_id} not found."
                )
            )

    # --------------------------------------------------
    # CREATE
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create(validated_data: dict) -> SalesInvoiceItem:
        invoice = validated_data["invoice"]
        variant = validated_data["variant"]

        if invoice.status not in {
            InvoiceStatus.DRAFT.value,
            InvoiceStatus.SENT.value,
        }:
            raise BusinessLogicException(
                message=(
                    "Items can only be added to draft or "
                    "sent invoices."
                )
            )

        if SalesInvoiceItem.objects.filter(
            invoice=invoice, variant=variant
        ).exists():
            raise ConflictException(
                message=(
                    "This variant already exists in the invoice."
                )
            )

        item = SalesInvoiceItem.objects.create(
            invoice=invoice,
            variant=variant,
            quantity=validated_data["quantity"],
            sale_price=validated_data["sale_price"],
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
    ) -> SalesInvoiceItem:
        item = SalesInvoiceItem.objects.select_for_update().get(
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
            "sale_price",
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
        item = SalesInvoiceItem.objects.select_for_update().get(
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
