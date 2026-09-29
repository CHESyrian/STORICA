"""
Custom JWT obtain view that records login history, sessions, and IP/UA.
"""

from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.services.user_service import UserService


def _client_ip(request) -> str | None:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _user_agent(request) -> str:
    return (request.META.get("HTTP_USER_AGENT") or "")[:2000]


class StoricaTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Extend default serializer with lockout check before auth."""

    def validate(self, attrs):
        username = attrs.get("username") or attrs.get(
            self.username_field, ""
        )
        request = self.context.get("request")

        if username and UserService.is_locked_out(username):
            UserService.record_login_failure(
                username=username,
                ip_address=_client_ip(request) if request else None,
                user_agent=_user_agent(request) if request else "",
                reason="Account temporarily locked",
            )
            from rest_framework_simplejwt.exceptions import (
                AuthenticationFailed,
            )

            raise AuthenticationFailed(
                "Too many failed login attempts. Try again later.",
                code="authorization",
            )

        try:
            data = super().validate(attrs)
        except Exception:
            if request is not None:
                UserService.record_login_failure(
                    username=username,
                    ip_address=_client_ip(request),
                    user_agent=_user_agent(request),
                    reason="Invalid credentials",
                )
            raise

        return data


class StoricaTokenObtainPairView(TokenObtainPairView):
    serializer_class = StoricaTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except Exception as exc:
            # SimpleJWT / DRF already shaped the error response.
            raise exc

        user = serializer.user
        refresh = serializer.validated_data["refresh"]
        access = serializer.validated_data["access"]

        # Decode refresh for expiry when possible
        expires_at = None
        try:
            token = RefreshToken(refresh)
            exp = token.get("exp")
            if exp:
                from django.utils import timezone
                from datetime import datetime, timezone as dt_tz

                expires_at = datetime.fromtimestamp(
                    exp, tz=dt_tz.utc
                )
                if timezone.is_naive(expires_at):
                    expires_at = timezone.make_aware(expires_at)
        except Exception:
            expires_at = None

        UserService.record_login_success(
            user,
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
            refresh_token=refresh,
            expires_at=expires_at,
        )

        return Response(
            {
                "access": access,
                "refresh": refresh,
            },
            status=status.HTTP_200_OK,
        )
