from rest_framework import serializers

from common.exceptions.base import ValidationException

from apps.purchases.models import Supplier


# =========================================================
# SUPPLIER LIST SERIALIZER
# =========================================================
class SupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "code",
            "slug",
            "name",
            "email",
            "phone",
            "is_verified",
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
# SUPPLIER DETAIL SERIALIZER
# =========================================================
class SupplierDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "id",
            "code",
            "slug",
            "name",
            "email",
            "phone",
            "address",
            "is_verified",
            "is_active",
            "notes",
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
# SUPPLIER CREATE SERIALIZER
# =========================================================
class SupplierCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "name",
            "email",
            "phone",
            "address",
            "is_verified",
            "notes",
        ]

    def validate_email(self, value):
        if value in (None, ""):
            return ""
        if Supplier.objects.filter(email=value).exists():
            raise ValidationException(
                message="A supplier with this email already exists."
            )
        return value

    def validate_phone(self, value):
        if Supplier.objects.filter(phone=value).exists():
            raise ValidationException(
                message="A supplier with this phone already exists."
            )
        return value

    def validate_name(self, value):
        if not value.strip():
            raise ValidationException(
                message="Supplier name cannot be blank."
            )
        return value.strip()


# =========================================================
# SUPPLIER UPDATE SERIALIZER
# =========================================================
class SupplierUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = [
            "name",
            "email",
            "phone",
            "address",
            "is_verified",
            "notes",
        ]

    def validate_email(self, value):
        if value in (None, ""):
            return ""
        instance = self.instance
        qs = Supplier.objects.filter(email=value).exclude(pk=instance.pk)
        if qs.exists():
            raise ValidationException(
                message="A supplier with this email already exists."
            )
        return value

    def validate_phone(self, value):
        instance = self.instance
        qs = Supplier.objects.filter(phone=value).exclude(pk=instance.pk)
        if qs.exists():
            raise ValidationException(
                message="A supplier with this phone already exists."
            )
        return value

    def validate_name(self, value):
        if not value.strip():
            raise ValidationException(
                message="Supplier name cannot be blank."
            )
        return value.strip()


# =========================================================
# SUPPLIER DELETE SERIALIZER
# =========================================================
class SupplierDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
