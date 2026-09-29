from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from common.api_response import ApiResponse
from common.permissions import (
    IsAuthenticatedAndActive,
    IsAdminRole,
)
from common.exceptions.base import BusinessLogicException

from apps.users.models import User
from apps.users.filters import UserFilter
from apps.users.services import UserService
from apps.users.serializers import (
    UserSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    AdminUserUpdateSerializer,
    ChangePasswordSerializer,
    AdminResetPasswordSerializer,
    UserSessionSerializer,
    UserLoginHistorySerializer,
)


class AuthViewSet(viewsets.ModelViewSet):
    """
    User management + session / profile actions.

    - Admin: full CRUD, reset password, revoke sessions
    - Any authenticated user: me, update profile, change password,
      list own sessions, logout
    """

    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = UserFilter
    search_fields = ["username", "email", "full_name"]
    ordering_fields = ["username", "created_at", "role", "last_login"]
    ordering = ["-created_at"]

    def get_permissions(self):
        admin_actions = {
            "create",
            "list",
            "retrieve",
            "destroy",
            "update",
            "partial_update",
            "reset_password",
            "revoke_sessions",
            "login_history",
        }
        if self.action in admin_actions:
            return [IsAuthenticatedAndActive(), IsAdminRole()]
        return [IsAuthenticatedAndActive()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        if self.action == "update_me":
            return UserUpdateSerializer
        if self.action in ("update", "partial_update"):
            return AdminUserUpdateSerializer
        if self.action == "change_password":
            return ChangePasswordSerializer
        if self.action == "reset_password":
            return AdminResetPasswordSerializer
        return UserSerializer

    # --------------------------------------------------
    # Admin CRUD via service
    # --------------------------------------------------
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = UserService.create_user(
            username=data["username"],
            password=data["password"],
            email=data.get("email"),
            full_name=data.get("full_name", ""),
            role=data.get("role", "user"),
            actor=request.user,
        )
        return ApiResponse.success(
            data=UserSerializer(user).data,
            message="User created",
            status_code=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        user = UserService.update_user(
            instance.pk,
            serializer.validated_data,
            actor=request.user,
            partial=partial,
        )
        return ApiResponse.success(data=UserSerializer(user).data)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Soft-deactivate rather than hard delete
        UserService.update_user(
            instance.pk,
            {"is_active": False},
            actor=request.user,
        )
        return ApiResponse.success(message="User deactivated")

    # --------------------------------------------------
    # Current user
    # --------------------------------------------------
    @action(detail=False, methods=["get"])
    def me(self, request):
        user = request.user
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name or user.username,
                "role": user.role,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "theme": user.theme,
                "language": user.language,
                "last_login": (
                    user.last_login.isoformat()
                    if user.last_login
                    else None
                ),
                "permissions": user.get_permissions_list(),
            }
        )

    @action(
        detail=False,
        methods=["put", "patch"],
        url_path="me/update",
    )
    def update_me(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        user = UserService.update_user(
            request.user.pk,
            serializer.validated_data,
            actor=request.user,
        )
        return Response(UserSerializer(user).data)

    # --------------------------------------------------
    # Password
    # --------------------------------------------------
    @action(
        detail=False,
        methods=["post"],
        url_path="me/change-password",
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            UserService.change_password(
                request.user,
                serializer.validated_data["old_password"],
                serializer.validated_data["new_password"],
            )
        except BusinessLogicException as exc:
            return ApiResponse.error(
                message=str(exc),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"message": "Password changed successfully"})

    @action(
        detail=True,
        methods=["post"],
        url_path="reset-password",
    )
    def reset_password(self, request, pk=None):
        user = self.get_object()
        serializer = AdminResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            UserService.admin_reset_password(
                user.pk,
                serializer.validated_data["new_password"],
                actor=request.user,
            )
        except BusinessLogicException as exc:
            return ApiResponse.error(
                message=str(exc),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        return ApiResponse.success(
            message="Password reset; active sessions revoked"
        )

    # --------------------------------------------------
    # Sessions / history
    # --------------------------------------------------
    @action(
        detail=False,
        methods=["get"],
        url_path="me/sessions",
    )
    def my_sessions(self, request):
        qs = UserService.list_active_sessions(request.user)
        return Response(UserSessionSerializer(qs, many=True).data)

    @action(
        detail=True,
        methods=["post"],
        url_path="revoke-sessions",
    )
    def revoke_sessions(self, request, pk=None):
        user = self.get_object()
        count = UserService.revoke_all_sessions(user)
        return ApiResponse.success(
            data={"revoked": count},
            message=f"Revoked {count} session(s)",
        )

    @action(
        detail=True,
        methods=["get"],
        url_path="login-history",
    )
    def login_history(self, request, pk=None):
        user = self.get_object()
        qs = user.login_history.all()[:50]
        return Response(
            UserLoginHistorySerializer(qs, many=True).data
        )

    # --------------------------------------------------
    # Auth helpers
    # --------------------------------------------------
    @action(detail=False, methods=["get"], url_path="verify")
    def verify(self, request):
        return Response(
            {
                "authenticated": True,
                "user_id": request.user.id,
                "username": request.user.username,
            }
        )

    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"refresh": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            UserService.deactivate_session_by_token(refresh_token)
            return Response(
                {
                    "success": True,
                    "message": "Logged out successfully",
                }
            )
        except TokenError:
            return Response(
                {
                    "success": False,
                    "message": "Invalid refresh token",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
