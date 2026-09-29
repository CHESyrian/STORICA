from rest_framework import serializers

from common.exceptions.base import ValidationException

from apps.sales.models import Customer


# =========================================================
# CUSTOMER LIST SERIALIZER
# =========================================================
class CustomerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
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
# CUSTOMER DETAIL SERIALIZER
# =========================================================
class CustomerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
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
# CUSTOMER CREATE SERIALIZER
# =========================================================
class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "name",
            "email",
            "phone",
            "address",
            "is_verified",
            "notes",
        ]

    def validate_name(self, value):
        if not value.strip():
            raise ValidationException(
                message="Customer name cannot be blank."
            )
        return value.strip()

    def validate_email(self, value):
        if value in (None, ""):
            return ""
        if Customer.objects.filter(email=value).exists():
            raise ValidationException(
                message="A customer with this email already exists."
            )
        return value

    def validate_phone(self, value):
        if Customer.objects.filter(phone=value).exists():
            raise ValidationException(
                message="A customer with this phone already exists."
            )
        return value


# =========================================================
# CUSTOMER UPDATE SERIALIZER
# =========================================================
class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = [
            "name",
            "email",
            "phone",
            "address",
            "is_verified",
            "notes",
        ]

    def validate_name(self, value):
        if not value.strip():
            raise ValidationException(
                message="Customer name cannot be blank."
            )
        return value.strip()

    def validate_email(self, value):
        if value in (None, ""):
            return ""
        qs = Customer.objects.filter(email=value).exclude(
            pk=self.instance.pk
        )
        if qs.exists():
            raise ValidationException(
                message="A customer with this email already exists."
            )
        return value

    def validate_phone(self, value):
        qs = Customer.objects.filter(phone=value).exclude(
            pk=self.instance.pk
        )
        if qs.exists():
            raise ValidationException(
                message="A customer with this phone already exists."
            )
        return value


# =========================================================
# CUSTOMER DELETE SERIALIZER
# =========================================================
class CustomerDeleteSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise ValidationException(
                message="You must confirm deletion."
            )
        return value
