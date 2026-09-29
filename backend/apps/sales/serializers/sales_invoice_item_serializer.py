from decimal import Decimal

from rest_framework import serializers

from common.exceptions.base import ValidationException

from apps.sales.models import SalesInvoiceItem


# =========================================================
# SALES INVOICE ITEM LIST SERIALIZER
# =========================================================
class SalesInvoiceItemListSerializer(serializers.ModelSerializer):
    invoice_code = serializers.CharField(
        source="invoice.code", read_only=True
    )
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = SalesInvoiceItem
        fields = [
            "id",
            "invoice",
            "invoice_code",
            "variant",
            "variant_name",
            "quantity",
            "sale_price",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "invoice_code",
            "variant_name",
            "created_at",
        ]


# =========================================================
# SALES INVOICE ITEM DETAIL SERIALIZER
# =========================================================
class SalesInvoiceItemDetailSerializer(serializers.ModelSerializer):
    invoice_code = serializers.CharField(
        source="invoice.code", read_only=True
    )
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = SalesInvoiceItem
        fields = [
            "id",
            "invoice",
            "invoice_code",
            "variant",
            "variant_name",
            "quantity",
            "sale_price",
            "discount_rate",
            "tax_rate",
            "notes",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "invoice_code",
            "variant_name",
            "created_at",
        ]


# =========================================================
# SALES INVOICE ITEM CREATE SERIALIZER
# =========================================================
class SalesInvoiceItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesInvoiceItem
        fields = [
            "invoice",
            "variant",
            "quantity",
            "sale_price",
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

    def validate_sale_price(self, value):
        if value < Decimal("0.00"):
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

    def validate(self, attrs):
        invoice = attrs.get("invoice")
        variant = attrs.get("variant")
        if SalesInvoiceItem.objects.filter(
            invoice=invoice, variant=variant
        ).exists():
            raise ValidationException(
                message=(
                    "This variant already exists in the invoice."
                )
            )
        return attrs


# =========================================================
# SALES INVOICE ITEM UPDATE SERIALIZER
# =========================================================
class SalesInvoiceItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesInvoiceItem
        fields = [
            "quantity",
            "sale_price",
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

    def validate_sale_price(self, value):
        if value < Decimal("0.00"):
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
# SALES INVOICE ITEM DELETE SERIALIZER
# =========================================================
class SalesInvoiceItemDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
