from rest_framework import serializers

from apps.users.models import User, UserRole, UserSession, UserLoginHistory


class UserSerializer(serializers.ModelSerializer):
    """User serializer for list/detail."""

    role_display = serializers.CharField(
        source="get_role_display", read_only=True
    )
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "role",
            "role_display",
            "is_active",
            "is_staff",
            "is_superuser",
            "theme",
            "language",
            "last_login",
            "last_login_ip",
            "date_joined",
            "created_at",
            "permissions",
        ]
        read_only_fields = [
            "id",
            "last_login",
            "last_login_ip",
            "date_joined",
            "created_at",
            "is_superuser",
            "is_staff",
        ]

    def get_permissions(self, obj):
        return obj.get_permissions_list()


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for admin-creating users."""

    password = serializers.CharField(
        write_only=True, required=True, min_length=8
    )
    confirm_password = serializers.CharField(
        write_only=True, required=True
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "full_name",
            "password",
            "confirm_password",
            "role",
        ]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        role = data.get("role", UserRole.USER)
        if role not in UserRole.values:
            raise serializers.ValidationError({"role": "Invalid role"})
        return data

    def create(self, validated_data):
        validated_data.pop("confirm_password")
        return validated_data


class UserUpdateSerializer(serializers.ModelSerializer):
    """Self-service profile update (no role / is_active)."""

    class Meta:
        model = User
        fields = ["email", "full_name", "theme", "language"]


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Admin update: may change role and is_active."""

    class Meta:
        model = User
        fields = [
            "email",
            "full_name",
            "theme",
            "language",
            "role",
            "is_active",
        ]

    def validate_role(self, value):
        if value not in UserRole.values:
            raise serializers.ValidationError("Invalid role")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "New passwords do not match"}
            )
        return data


class AdminResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match"}
            )
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = [
            "id",
            "ip_address",
            "user_agent",
            "created_at",
            "expires_at",
            "last_activity",
            "is_active",
        ]


class UserLoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLoginHistory
        fields = [
            "id",
            "login_time",
            "ip_address",
            "user_agent",
            "success",
            "failure_reason",
        ]
