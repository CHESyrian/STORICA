from decimal import Decimal

from rest_framework import serializers

from common.exceptions.base import ValidationException
from common.models.choices import InvoiceStatus

from apps.sales.models import SalesInvoice, SalesInvoiceItem


# =========================================================
# INVOICE ITEM NESTED SERIALIZERS
# =========================================================
class SalesInvoiceItemNestedSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = SalesInvoiceItem
        fields = [
            "id",
            "variant",
            "variant_name",
            "quantity",
            "sale_price",
            "discount_rate",
            "tax_rate",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "variant_name", "created_at"]


class SalesInvoiceItemWriteSerializer(serializers.ModelSerializer):
    # Accept unit_price as alias (frontend invoice form uses that label)
    unit_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False, write_only=True
    )
    sale_price = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )

    class Meta:
        model = SalesInvoiceItem
        fields = [
            "variant",
            "quantity",
            "sale_price",
            "unit_price",
            "discount_rate",
            "tax_rate",
            "notes",
        ]

    def validate_quantity(self, value):
        if value < Decimal("0.01"):
            raise ValidationException(
                message="Quantity must be greater than 0."
            )
        return value

    def validate(self, attrs):
        price = attrs.get("sale_price")
        if price is None:
            price = attrs.get("unit_price")
        if price is None:
            raise ValidationException(
                message="Sale price is required."
            )
        if price < Decimal("0.00"):
            raise ValidationException(
                message="Sale price cannot be negative."
            )
        attrs["sale_price"] = price
        attrs.pop("unit_price", None)
        return attrs

    def validate_sale_price(self, value):
        if value is not None and value < Decimal("0.00"):
            raise ValidationException(
                message="Sale price cannot be negative."
            )
        return value

    def validate_discount_rate(self, value):
        if not (Decimal("0") <= value <= Decimal("100")):
            raise ValidationException(
                message="Discount rate must be between 0 and 100."
            )
        return value

    def validate_tax_rate(self, value):
        if not (Decimal("0") <= value <= Decimal("100")):
            raise ValidationException(
                message="Tax rate must be between 0 and 100."
            )
        return value


# =========================================================
# SALES INVOICE LIST SERIALIZER
# =========================================================
class SalesInvoiceListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name", read_only=True
    )

    class Meta:
        model = SalesInvoice
        fields = [
            "id",
            "code",
            "customer",
            "customer_name",
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
            "customer_name",
            "created_at",
        ]


# =========================================================
# SALES INVOICE DETAIL SERIALIZER
# =========================================================
class SalesInvoiceDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name", read_only=True
    )
    items = SalesInvoiceItemNestedSerializer(many=True, read_only=True)

    class Meta:
        model = SalesInvoice
        fields = [
            "id",
            "code",
            "customer",
            "customer_name",
            "order",
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
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "customer_name",
            "paid_date",
            "items",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


# =========================================================
# SALES INVOICE CREATE SERIALIZER
# =========================================================
class SalesInvoiceCreateSerializer(serializers.ModelSerializer):
    items = SalesInvoiceItemWriteSerializer(many=True)

    class Meta:
        model = SalesInvoice
        fields = [
            "customer",
            "order",
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
# SALES INVOICE UPDATE SERIALIZER
# =========================================================
class SalesInvoiceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesInvoice
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
# SALES INVOICE DELETE SERIALIZER
# =========================================================
class SalesInvoiceDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
