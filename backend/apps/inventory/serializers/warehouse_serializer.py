from rest_framework import serializers

from common.exceptions.base import ValidationException
from common.models.choices import WarehouseStatus

from apps.inventory.models import Warehouse


# =========================================================
# WAREHOUSE LIST SERIALIZER
# =========================================================
class WarehouseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = [
            "id",
            "code",
            "slug",
            "name",
            "location",
            "phone",
            "status",
            "is_active",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "code",
            "slug",
            "created_at",
        ]


# =========================================================
# WAREHOUSE DETAIL SERIALIZER
# =========================================================
class WarehouseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = [
            "id",
            "code",
            "slug",
            "name",
            "description",
            "location",
            "phone",
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
            "created_by",
            "updated_by",
            "created_at",
            "updated_at",
        ]


# =========================================================
# WAREHOUSE CREATE SERIALIZER
# =========================================================
class WarehouseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = [
            "name",
            "description",
            "location",
            "phone",
            "status",
        ]

    def validate_name(self, value):
        if not value.strip():
            raise ValidationException(
                message="Warehouse name cannot be blank."
            )
        if Warehouse.objects.filter(name=value.strip()).exists():
            raise ValidationException(
                message="A warehouse with this name already exists."
            )
        return value.strip()

    def validate_status(self, value):
        valid = [choice[0] for choice in WarehouseStatus.choices]
        if value not in valid:
            raise ValidationException(
                message=f"Invalid status. Choices: {valid}."
            )
        return value


# =========================================================
# WAREHOUSE UPDATE SERIALIZER
# =========================================================
class WarehouseUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = [
            "name",
            "description",
            "location",
            "phone",
            "status",
        ]

    def validate_name(self, value):
        if not value.strip():
            raise ValidationException(
                message="Warehouse name cannot be blank."
            )
        qs = Warehouse.objects.filter(
            name=value.strip()
        ).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationException(
                message="A warehouse with this name already exists."
            )
        return value.strip()

    def validate_status(self, value):
        valid = [choice[0] for choice in WarehouseStatus.choices]
        if value not in valid:
            raise ValidationException(
                message=f"Invalid status. Choices: {valid}."
            )
        return value


# =========================================================
# WAREHOUSE DELETE SERIALIZER
# =========================================================
class WarehouseDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
