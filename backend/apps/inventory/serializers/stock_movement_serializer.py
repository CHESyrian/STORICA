from decimal import Decimal

from rest_framework import serializers

from common.exceptions.base import ValidationException
from common.models.choices import StockMovementType, MovementStatus

from apps.inventory.models import StockMovement


# =========================================================
# STOCK MOVEMENT LIST SERIALIZER
# =========================================================
class StockMovementListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name", read_only=True
    )
    batch_code = serializers.CharField(
        source="batch.code", read_only=True, default=None
    )
    from_warehouse_name = serializers.CharField(
        source="from_warehouse.name", read_only=True, default=None
    )
    to_warehouse_name = serializers.CharField(
        source="to_warehouse.name", read_only=True, default=None
    )
    movement_type_display = serializers.CharField(
        source="get_movement_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "movement_id",
            "movement_type",
            "movement_type_display",
            "status",
            "status_display",
            "product",
            "product_name",
            "batch",
            "batch_code",
            "from_warehouse",
            "from_warehouse_name",
            "to_warehouse",
            "to_warehouse_name",
            "quantity",
            "unit_price",
            "reference_number",
            "movement_date",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "movement_id",
            "movement_type_display",
            "status_display",
            "product_name",
            "batch_code",
            "from_warehouse_name",
            "to_warehouse_name",
            "created_at",
        ]



# =========================================================
# STOCK MOVEMENT DETAIL SERIALIZER
# =========================================================
class StockMovementDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name", read_only=True
    )
    product_sku = serializers.CharField(
        source="product.sku", read_only=True
    )
    batch_code = serializers.CharField(
        source="batch.code", read_only=True
    )
    from_warehouse_name = serializers.CharField(
        source="from_warehouse.name", read_only=True
    )
    to_warehouse_name = serializers.CharField(
        source="to_warehouse.name", read_only=True
    )
    performed_by_name = serializers.CharField(
        source="performed_by.get_full_name", read_only=True
    )
    approved_by_name = serializers.CharField(
        source="approved_by.get_full_name", read_only=True
    )
    movement_type_display = serializers.CharField(
        source="get_movement_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    total_cost = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True,
    )

    class Meta:
        model = StockMovement
        fields = [
            "id",
            "movement_id",
            "movement_type",
            "movement_type_display",
            "status",
            "status_display",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "unit_price",
            "total_cost",
            "batch",
            "batch_code",
            "from_warehouse",
            "from_warehouse_name",
            "to_warehouse",
            "to_warehouse_name",
            "reference_number",
            "notes",
            "performed_by",
            "performed_by_name",
            "approved_by",
            "approved_by_name",
            "movement_date",
            "completed_at",
            "created_by",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "movement_id",
            "product_name",
            "product_sku",
            "batch_code",
            "from_warehouse_name",
            "to_warehouse_name",
            "performed_by_name",
            "approved_by_name",
            "movement_type_display",
            "status_display",
            "total_cost",
            "completed_at",
            "created_at",
        ]


# =========================================================
# STOCK MOVEMENT CREATE SERIALIZER
# =========================================================
class StockMovementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = [
            "movement_type",
            "product",
            "quantity",
            "unit_price",
            "batch",
            "from_warehouse",
            "to_warehouse",
            "reference_number",
            "notes",
            "performed_by",
            "movement_date",
            "created_by",
        ]

    def validate_quantity(self, value):
        if value <= Decimal("0"):
            raise ValidationException(
                message="Movement quantity must be greater than 0."
            )
        return value

    def validate_unit_price(self, value):
        if value < Decimal("0"):
            raise ValidationException(
                message="Unit price cannot be negative."
            )
        return value

    def validate_movement_type(self, value):
        valid = [choice[0] for choice in StockMovementType.choices]
        if value not in valid:
            raise ValidationException(
                message=f"Invalid movement type. Choices: {valid}."
            )
        return value

    def validate(self, attrs):
        movement_type = attrs.get("movement_type")
        from_wh = attrs.get("from_warehouse")
        to_wh = attrs.get("to_warehouse")

        if movement_type == StockMovementType.IN and not to_wh:
            raise ValidationException(
                message=(
                    "to_warehouse is required for stock-in movements."
                )
            )

        if movement_type == StockMovementType.OUT and not from_wh:
            raise ValidationException(
                message=(
                    "from_warehouse is required for stock-out "
                    "movements."
                )
            )

        if movement_type == StockMovementType.TRANSFER:
            if not from_wh or not to_wh:
                raise ValidationException(
                    message=(
                        "Both from_warehouse and to_warehouse are "
                        "required for transfer movements."
                    )
                )
            if from_wh == to_wh:
                raise ValidationException(
                    message=(
                        "from_warehouse and to_warehouse must be "
                        "different for transfers."
                    )
                )

        return attrs


# =========================================================
# STOCK MOVEMENT UPDATE SERIALIZER
# =========================================================
class StockMovementUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = [
            "status",
            "approved_by",
            "reference_number",
            "notes",
        ]

    def validate_status(self, value):
        valid = [choice[0] for choice in MovementStatus.choices]
        if value not in valid:
            raise ValidationException(
                message=f"Invalid status. Choices: {valid}."
            )
        instance = self.instance
        if (
            instance
            and instance.status == MovementStatus.COMPLETED
            and value != MovementStatus.CANCELLED
        ):
            raise ValidationException(
                message=(
                    "A completed movement cannot change status "
                    "except to cancelled."
                )
            )
        return value


# =========================================================
# STOCK MOVEMENT DELETE SERIALIZER
# =========================================================
class StockMovementDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
