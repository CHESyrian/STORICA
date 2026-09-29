from decimal import Decimal

from rest_framework import serializers

from common.exceptions.base import ValidationException
from common.models.choices import PaymentStatus

from apps.purchases.models import PurchasesPayment


# =========================================================
# PAYMENT LIST SERIALIZER
# =========================================================
class PurchasesPaymentListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.name", read_only=True
    )
    invoice_code = serializers.CharField(
        source="invoice.code", read_only=True
    )

    class Meta:
        model = PurchasesPayment
        fields = [
            "id",
            "payment_id",
            "transaction_id",
            "invoice",
            "invoice_code",
            "supplier",
            "supplier_name",
            "amount",
            "payment_date",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "payment_id",
            "invoice_code",
            "supplier_name",
            "created_at",
        ]


# =========================================================
# PAYMENT DETAIL SERIALIZER
# =========================================================
class PurchasesPaymentDetailSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source="supplier.name", read_only=True
    )
    invoice_code = serializers.CharField(
        source="invoice.code", read_only=True
    )
    processed_by_name = serializers.CharField(
        source="processed_by.get_full_name", read_only=True
    )

    class Meta:
        model = PurchasesPayment
        fields = [
            "id",
            "payment_id",
            "transaction_id",
            "invoice",
            "invoice_code",
            "order",
            "supplier",
            "supplier_name",
            "amount",
            "payment_date",
            "status",
            "reference_number",
            "notes",
            "processed_by",
            "processed_by_name",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "payment_id",
            "invoice_code",
            "supplier_name",
            "processed_by_name",
            "created_at",
        ]


# =========================================================
# PAYMENT CREATE SERIALIZER
# =========================================================
class PurchasesPaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesPayment
        fields = [
            "invoice",
            "order",
            "supplier",
            "amount",
            "payment_date",
            "reference_number",
            "notes",
        ]

    def validate_amount(self, value):
        if value < Decimal("0.01"):
            raise ValidationException(
                message="Payment amount must be greater than 0."
            )
        return value

    def validate_transaction_id(self, value):
        if value and PurchasesPayment.objects.filter(
            transaction_id=value
        ).exists():
            raise ValidationException(
                message="A payment with this transaction ID already exists."
            )
        return value

    def validate(self, attrs):
        invoice = attrs.get("invoice")
        amount = attrs.get("amount", Decimal("0"))
        if invoice:
            remaining = invoice.total_amount - invoice.amount_paid
            if amount > remaining:
                raise ValidationException(
                    message=(
                        f"Payment amount ({amount}) exceeds "
                        f"remaining balance ({remaining})."
                    )
                )
        return attrs


# =========================================================
# PAYMENT UPDATE SERIALIZER
# =========================================================
class PurchasesPaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchasesPayment
        fields = [
            "status",
            "reference_number",
            "notes",
        ]

    def validate_status(self, value):
        instance = self.instance
        if (
            instance
            and instance.status == PaymentStatus.COMPLETED.value
            and value != PaymentStatus.REFUNDED.value
        ):
            raise ValidationException(
                message=(
                    "A completed payment can only be set to refunded."
                )
            )
        return value


# =========================================================
# PAYMENT DELETE SERIALIZER
# =========================================================
class PurchasesPaymentDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
