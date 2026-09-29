from decimal import Decimal

from rest_framework import serializers

from common.exceptions.base import ValidationException
from common.models.choices import BatchStatus

from apps.inventory.models import Batch


# =========================================================
# BATCH LIST SERIALIZER
# =========================================================
class BatchListSerializer(serializers.ModelSerializer):
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )
    variant_sku = serializers.CharField(
        source="variant.sku", read_only=True
    )
    warehouse_name = serializers.CharField(
        source="warehouse.name", read_only=True
    )

    class Meta:
        model = Batch
        fields = [
            "id",
            "code",
            "slug",
            "variant",
            "variant_name", 
            "variant_sku",
            "warehouse",
            "warehouse_name",
            "quantity",
            "cost_price",
            "production_date",
            "expiry_date",
            "status",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "slug",
            "variant_name", 
            "variant_sku",
            "warehouse_name",
            "created_at",
        ]


# =========================================================
# BATCH DETAIL SERIALIZER
# =========================================================
class BatchDetailSerializer(serializers.ModelSerializer):
    variant_sku = serializers.CharField(
        source="variant.sku", read_only=True
    )
    variant_name = serializers.CharField(
        source="variant.name", read_only=True
    )
    warehouse_name = serializers.CharField(
        source="warehouse.name", read_only=True
    )

    class Meta:
        model = Batch
        fields = [
            "id",
            "code",
            "slug",
            "variant",
            "variant_sku",
            "variant_name",
            "warehouse",
            "warehouse_name",
            "quantity",
            "cost_price",
            "production_date",
            "expiry_date",
            "received_date",
            "status",
            "is_active",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "slug",
            "variant_sku",
            "variant_name",
            "warehouse_name",
            "received_date",
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


# =========================================================
# BATCH CREATE SERIALIZER
# =========================================================
class BatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = [
            "variant",
            "warehouse",
            "quantity",
            "cost_price",
            "production_date",
            "expiry_date",
            "status",
        ]

    def validate_quantity(self, value):
        if value <= Decimal("0"):
            raise ValidationException(
                message="Batch quantity must be greater than 0."
            )
        return value

    def validate_cost_price(self, value):
        if value < Decimal("0"):
            raise ValidationException(
                message="Cost price cannot be negative."
            )
        return value

    def validate_variant(self, value):
        if not value.is_active:
            raise ValidationException(
                message="Cannot create a batch for an inactive variant."
            )
        return value

    def validate_warehouse(self, value):
        if not value.is_active:
            raise ValidationException(
                message=(
                    "Cannot create a batch in an inactive warehouse."
                )
            )
        return value

    def validate(self, attrs):
        production_date = attrs.get("production_date")
        expiry_date = attrs.get("expiry_date")
        if production_date and expiry_date:
            if expiry_date <= production_date:
                raise ValidationException(
                    message=(
                        "Expiry date must be after production date."
                    )
                )
        return attrs


# =========================================================
# BATCH UPDATE SERIALIZER
# =========================================================
class BatchUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = [
            "quantity",
            "cost_price",
            "production_date",
            "expiry_date",
            "status",
        ]

    def validate_quantity(self, value):
        if value <= Decimal("0"):
            raise ValidationException(
                message="Batch quantity must be greater than 0."
            )
        return value

    def validate_cost_price(self, value):
        if value < Decimal("0"):
            raise ValidationException(
                message="Cost price cannot be negative."
            )
        return value

    def validate_status(self, value):
        valid = [choice[0] for choice in BatchStatus.choices]
        if value not in valid:
            raise ValidationException(
                message=f"Invalid status. Choices: {valid}."
            )
        return value

    def validate(self, attrs):
        instance = self.instance
        production_date = attrs.get(
            "production_date",
            instance.production_date if instance else None,
        )
        expiry_date = attrs.get(
            "expiry_date",
            instance.expiry_date if instance else None,
        )
        if production_date and expiry_date:
            if expiry_date <= production_date:
                raise ValidationException(
                    message=(
                        "Expiry date must be after production date."
                    )
                )
        return attrs


# =========================================================
# BATCH DELETE SERIALIZER
# =========================================================
class BatchDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
