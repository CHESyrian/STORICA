from decimal import Decimal

from rest_framework import serializers

from common.exceptions.base import ValidationException
from common.models.choices import PaymentStatus

from apps.sales.models import SalesPayment


# =========================================================
# SALES PAYMENT LIST SERIALIZER
# =========================================================
class SalesPaymentListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name", read_only=True
    )
    invoice_code = serializers.CharField(
        source="invoice.code", read_only=True
    )

    class Meta:
        model = SalesPayment
        fields = [
            "id",
            "payment_id",
            "transaction_id",
            "invoice",
            "invoice_code",
            "customer",
            "customer_name",
            "amount",
            "payment_date",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "payment_id",
            "invoice_code",
            "customer_name",
            "created_at",
        ]


# =========================================================
# SALES PAYMENT DETAIL SERIALIZER
# =========================================================
class SalesPaymentDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(
        source="customer.name", read_only=True
    )
    invoice_code = serializers.CharField(
        source="invoice.code", read_only=True
    )
    processed_by_name = serializers.CharField(
        source="processed_by.get_full_name", read_only=True
    )

    class Meta:
        model = SalesPayment
        fields = [
            "id",
            "payment_id",
            "transaction_id",
            "invoice",
            "invoice_code",
            "order",
            "customer",
            "customer_name",
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
            "customer_name",
            "processed_by_name",
            "created_at",
        ]


# =========================================================
# SALES PAYMENT CREATE SERIALIZER
# =========================================================
class SalesPaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesPayment
        fields = [
            "transaction_id",
            "invoice",
            "order",
            "customer",
            "amount",
            "payment_date",
            "reference_number",
            "notes",
            "processed_by",
        ]

    def validate_amount(self, value):
        if value < Decimal("0.01"):
            raise ValidationException(
                message="Payment amount must be greater than 0."
            )
        return value

    def validate_transaction_id(self, value):
        if value and SalesPayment.objects.filter(
            transaction_id=value
        ).exists():
            raise ValidationException(
                message=(
                    "A payment with this transaction ID "
                    "already exists."
                )
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
# SALES PAYMENT UPDATE SERIALIZER
# =========================================================
class SalesPaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesPayment
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
                    "A completed payment can only be "
                    "set to refunded."
                )
            )
        return value


# =========================================================
# SALES PAYMENT DELETE SERIALIZER
# =========================================================
class SalesPaymentDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
