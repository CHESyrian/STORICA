from decimal import Decimal

from rest_framework import serializers

from common.exceptions.base import ValidationException
from common.models.choices import InvoiceStatus

from apps.purchases.models import (
    PurchasesInvoice, PurchasesInvoiceItem
)
from .purchases_invoice_item_serializer import (
    PurchasesInvoiceItemNestedSerializer, 
    PurchasesInvoiceItemWriteSerializer
)


# =========================================================
# INVOICE LIST SERIALIZER
# =========================================================
class PurchasesInvoiceListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.name", read_only=True
    )
    warehouse_name = serializers.CharField(
        source="warehouse.name", read_only=True
    )

    class Meta:
        model = PurchasesInvoice
        fields = [
            "id",
            "code",
            "supplier",
            "supplier_name",
            "warehouse", 
            "warehouse_name", 
            "order",
            "invoice_date",
            "status",
            "total_amount",
            "amount_paid",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "supplier_name",
            "created_at",
        ]


# =========================================================
# INVOICE DETAIL SERIALIZER
# =========================================================
class PurchasesInvoiceDetailSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.name", read_only=True
    )
    warehouse_name = serializers.CharField(
        source="warehouse.name", read_only=True
    )
    order_code = serializers.CharField(
        source="order.code", read_only=True
    )
    created_by_name = serializers.CharField(
        source="created_by.username", read_only=True
    )
    updated_by_name = serializers.CharField(
        source="updated_by.username", read_only=True
    )

    items = PurchasesInvoiceItemNestedSerializer(many=True, read_only=True)

    class Meta:
        model = PurchasesInvoice
        fields = [
            "id",
            "code",
            "supplier",
            "supplier_name",
            "warehouse", 
            "warehouse_name", 
            "order",
            "order_code", 
            "invoice_date",
            "paid_date",
            "status",
            "discount_rate",
            "tax_rate",
            "total_amount",
            "amount_paid",
            "is_active",
            "notes",
            "items",
            "created_by",
            "created_by_name", 
            "updated_by", 
            "updated_by_name", 
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "supplier_name",
            "paid_date",
            "items",
            "created_by",
            "created_by_name", 
            "updated_by", 
            "updated_by_name", 
            "created_at",
            "updated_at",
        ]


# =========================================================
# INVOICE CREATE SERIALIZER
# =========================================================
class PurchasesInvoiceCreateSerializer(serializers.ModelSerializer):
    items = PurchasesInvoiceItemWriteSerializer(many=True)

    class Meta:
        model = PurchasesInvoice
        fields = [
            "supplier",
            "order",
            "warehouse", 
            "invoice_date",
            "discount_rate",
            "tax_rate",
            "total_amount",
            "amount_paid",
            "notes",
            "items",
        ]

    def validate_total_amount(self, value):
        if value <= Decimal("0"):
            raise ValidationException(
                message="Total amount must be greater than 0."
            )
        return value

    def validate_amount_paid(self, value):
        if value < Decimal("0"):
            raise ValidationException(
                message="Amount paid cannot be negative."
            )
        return value

    def validate_items(self, value):
        if not value:
            raise ValidationException(
                message="Invoice must have at least one item."
            )
        variant_ids = [item["variant"].pk for item in value]
        if len(variant_ids) != len(set(variant_ids)):
            raise ValidationException(
                message=(
                    "Duplicate variants are not allowed "
                    "in the same invoice."
                )
            )
        return value

    def validate(self, attrs):
        amount_paid = attrs.get("amount_paid", Decimal("0"))
        total_amount = attrs.get("total_amount")
        if total_amount and amount_paid > total_amount:
            raise ValidationException(
                message="Amount paid cannot exceed total amount."
            )
        return attrs


# =========================================================
# INVOICE UPDATE SERIALIZER
# =========================================================
class PurchasesInvoiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesInvoice
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

    def validate_total_amount(self, value):
        if value <= Decimal("0"):
            raise ValidationException(
                message="Total amount must be greater than 0."
            )
        return value

    def validate_amount_paid(self, value):
        if value < Decimal("0"):
            raise ValidationException(
                message="Amount paid cannot be negative."
            )
        return value

    def validate(self, attrs):
        instance = self.instance
        if (
            instance
            and instance.status == InvoiceStatus.CANCELLED.value
        ):
            raise ValidationException(
                message="Cannot update a cancelled invoice."
            )
        amount_paid = attrs.get(
            "amount_paid",
            instance.amount_paid if instance else Decimal("0"),
        )
        total_amount = attrs.get(
            "total_amount",
            instance.total_amount if instance else None,
        )
        if total_amount and amount_paid > total_amount:
            raise ValidationException(
                message="Amount paid cannot exceed total amount."
            )
        return attrs


# =========================================================
# INVOICE DELETE SERIALIZER
# =========================================================
class PurchasesInvoiceDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
