from decimal import Decimal

from rest_framework import serializers

from common.exceptions.base import ValidationException

from apps.purchases.models import PurchasesInvoiceItem


# =========================================================
# INVOICE ITEM LIST SERIALIZER
# =========================================================
class PurchasesInvoiceItemListSerializer(serializers.ModelSerializer):
    invoice_code = serializers.CharField(
        source="invoice.code", read_only=True
    )
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = PurchasesInvoiceItem
        fields = [
            "id",
            "invoice",
            "invoice_code",
            "variant",
            "variant_name",
            "quantity",
            "cost_price",
            "production_date", 
            "expiry_date", 
            "created_at",
        ]
        read_only_fields = [
            "id",
            "invoice_code",
            "variant_name",
            "created_at",
        ]


# =========================================================
# INVOICE ITEM DETAIL SERIALIZER
# =========================================================
class PurchasesInvoiceItemDetailSerializer(serializers.ModelSerializer):
    invoice_code = serializers.CharField(
        source="invoice.code", read_only=True
    )
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = PurchasesInvoiceItem
        fields = [
            "id",
            "invoice",
            "invoice_code",
            "variant",
            "variant_name",
            "quantity",
            "cost_price",
            "discount_rate",
            "tax_rate",
            "notes",
            "production_date", 
            "expiry_date",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "invoice_code",
            "variant_name",
            "created_at",
        ]


# =========================================================
# INVOICE ITEM CREATE SERIALIZER
# =========================================================
class PurchasesInvoiceItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesInvoiceItem
        fields = [
            "invoice",
            "variant",
            "quantity",
            "cost_price",
            "discount_rate",
            "tax_rate",
            "notes",
            "production_date", 
            "expiry_date",
        ]

    def validate_quantity(self, value):
        if value < Decimal("0.01"):
            raise ValidationException(
                message="Quantity must be greater than 0."
            )
        return value

    def validate_cost_price(self, value):
        if value < Decimal("0.00"):
            raise ValidationException(
                message="Cost price cannot be negative."
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
        if PurchasesInvoiceItem.objects.filter(
            invoice=invoice, variant=variant
        ).exists():
            raise ValidationException(
                message=(
                    "This variant already exists in the invoice."
                )
            )

        production_date = attrs.get("production_date")
        expiry_date = attrs.get("expiry_date")
        if expiry_date <= production_date:
            raise ValidationException(
                    message=(
                        "Expiry date must be after production date."
                    )
                )


        return attrs


# =========================================================
# INVOICE ITEM UPDATE SERIALIZER
# =========================================================
class PurchasesInvoiceItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesInvoiceItem
        fields = [
            "quantity",
            "cost_price",
            "discount_rate",
            "tax_rate",
            "production_date", 
            "expiry_date",
            "notes",
        ]

    def validate_quantity(self, value):
        if value < Decimal("0.01"):
            raise ValidationException(
                message="Quantity must be greater than 0."
            )
        return value

    def validate_cost_price(self, value):
        if value < Decimal("0.00"):
            raise ValidationException(
                message="Cost price cannot be negative."
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
# INVOICE ITEM DELETE SERIALIZER
# =========================================================
class PurchasesInvoiceItemDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value


# =========================================================
# INVOICE ITEM NESTED SERIALIZERS
# =========================================================
class PurchasesInvoiceItemNestedSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )

    class Meta:
        model = PurchasesInvoiceItem
        fields = [
            "id",
            "variant",
            "variant_name",
            "quantity",
            "cost_price",
            "discount_rate",
            "tax_rate",
            "production_date", 
            "expiry_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "variant_name", "created_at"]


class PurchasesInvoiceItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesInvoiceItem
        fields = [
            "variant",
            "quantity",
            "cost_price",
            "discount_rate",
            "tax_rate",
            "production_date", 
            "expiry_date",
            "notes",
        ]

    def validate_quantity(self, value):
        if value < Decimal("0.01"):
            raise ValidationException(
                message="Quantity must be greater than 0."
            )
        return value

    def validate_cost_price(self, value):
        if value < Decimal("0.00"):
            raise ValidationException(
                message="Cost price cannot be negative."
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
        if PurchasesInvoiceItem.objects.filter(
            invoice=invoice, variant=variant
        ).exists():
            raise ValidationException(
                message=(
                    "This variant already exists in the invoice."
                )
            )

        production_date = attrs.get("production_date")
        expiry_date     = attrs.get("expiry_date")
        if expiry_date <= production_date:
            raise ValidationException(
                    message=(
                        "Expiry date must be after production date."
                    )
                )


        return attrs

