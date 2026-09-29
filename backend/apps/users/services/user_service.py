"""
UserService — business logic for user admin, sessions, and login audit.
"""

from __future__ import annotations

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from common.exceptions.base import (
    BusinessLogicException,
    NotFoundException,
)
from common.permissions import ROLE_RANK

from apps.users.models import (
    User,
    UserLoginHistory,
    UserRole,
    UserSession,
)


# Failed logins within this window trigger lockout.
LOCKOUT_WINDOW = timedelta(minutes=15)
MAX_FAILED_ATTEMPTS = 5


class UserService:

    # --------------------------------------------------
    # Retrieve
    # --------------------------------------------------
    @staticmethod
    def get_by_id(user_id: int) -> User:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise NotFoundException(
                message=f"User with id {user_id} not found."
            )

    # --------------------------------------------------
    # Create / update
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def create_user(
        *,
        username: str,
        password: str,
        email: str | None = None,
        full_name: str = "",
        role: str = UserRole.USER,
        actor: User | None = None,
    ) -> User:
        """
        Create a user. Only admins may assign role=admin.
        Non-admins (if ever allowed) cannot escalate.
        """
        if role == UserRole.ADMIN:
            if not actor or not (
                actor.is_superuser or actor.role == UserRole.ADMIN
            ):
                raise BusinessLogicException(
                    message="Only administrators can create admin users."
                )

        if role not in UserRole.values:
            raise BusinessLogicException(message=f"Invalid role: {role}")

        if User.objects.filter(username__iexact=username).exists():
            raise BusinessLogicException(
                message="A user with this username already exists."
            )
        if email and User.objects.filter(email__iexact=email).exists():
            raise BusinessLogicException(
                message="A user with this email already exists."
            )

        user = User(
            username=username,
            email=email or None,
            full_name=full_name or "",
            role=role,
            is_active=True,
        )
        if role == UserRole.ADMIN:
            user.is_staff = True
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    @transaction.atomic
    def update_user(
        user_id: int,
        data: dict,
        *,
        actor: User | None = None,
        partial: bool = True,
    ) -> User:
        user = User.objects.select_for_update().get(pk=user_id)

        # Role changes are admin-only and cannot demote the last admin.
        if "role" in data and data["role"] is not None:
            if not actor or not (
                actor.is_superuser or actor.role == UserRole.ADMIN
            ):
                raise BusinessLogicException(
                    message="Only administrators can change roles."
                )
            new_role = data["role"]
            if new_role not in UserRole.values:
                raise BusinessLogicException(
                    message=f"Invalid role: {new_role}"
                )
            if (
                user.role == UserRole.ADMIN
                and new_role != UserRole.ADMIN
                and not UserService._has_other_admins(user)
            ):
                raise BusinessLogicException(
                    message="Cannot demote the last administrator."
                )
            user.role = new_role
            if new_role == UserRole.ADMIN:
                user.is_staff = True

        for field in ("email", "full_name", "theme", "language", "is_active"):
            if field in data:
                setattr(user, field, data[field])

        if data.get("is_active") is False:
            if user.pk == getattr(actor, "pk", None):
                raise BusinessLogicException(
                    message="You cannot deactivate your own account."
                )
            if (
                user.role == UserRole.ADMIN
                and not UserService._has_other_admins(user)
            ):
                raise BusinessLogicException(
                    message="Cannot deactivate the last administrator."
                )

        user.save()
        return user

    @staticmethod
    def _has_other_admins(exclude: User) -> bool:
        return (
            User.objects.filter(
                role=UserRole.ADMIN, is_active=True
            )
            .exclude(pk=exclude.pk)
            .exists()
            or User.objects.filter(
                is_superuser=True, is_active=True
            )
            .exclude(pk=exclude.pk)
            .exists()
        )

    # --------------------------------------------------
    # Password
    # --------------------------------------------------
    @staticmethod
    @transaction.atomic
    def change_password(
        user: User, old_password: str, new_password: str
    ) -> None:
        if not user.check_password(old_password):
            raise BusinessLogicException(message="Wrong current password.")
        if len(new_password) < 8:
            raise BusinessLogicException(
                message="New password must be at least 8 characters."
            )
        user.set_password(new_password)
        user.save(update_fields=["password"])

    @staticmethod
    @transaction.atomic
    def admin_reset_password(
        user_id: int,
        new_password: str,
        *,
        actor: User,
    ) -> User:
        if not (actor.is_superuser or actor.role == UserRole.ADMIN):
            raise BusinessLogicException(
                message="Only administrators can reset passwords."
            )
        if len(new_password) < 8:
            raise BusinessLogicException(
                message="New password must be at least 8 characters."
            )
        user = User.objects.select_for_update().get(pk=user_id)
        user.set_password(new_password)
        user.save(update_fields=["password"])
        # Invalidate active sessions for this user
        UserService.revoke_all_sessions(user)
        return user

    # --------------------------------------------------
    # Login audit + sessions
    # --------------------------------------------------
    @staticmethod
    def is_locked_out(username: str) -> bool:
        """True if too many failed logins for this username recently."""
        since = timezone.now() - LOCKOUT_WINDOW
        failures = UserLoginHistory.objects.filter(
            user__username__iexact=username,
            success=False,
            login_time__gte=since,
        ).count()
        # Also count attempts for unknown usernames stored with user=null
        # — we only lock known users.
        return failures >= MAX_FAILED_ATTEMPTS

    @staticmethod
    def record_login_success(
        user: User,
        *,
        ip_address: str | None = None,
        user_agent: str = "",
        refresh_token: str = "",
        expires_at=None,
    ) -> UserSession | None:
        UserLoginHistory.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent or "",
            success=True,
        )
        update_fields = []
        if ip_address:
            user.last_login_ip = ip_address
            update_fields.append("last_login_ip")
        if user_agent is not None:
            user.last_login_user_agent = user_agent or ""
            update_fields.append("last_login_user_agent")
        if update_fields:
            user.save(update_fields=update_fields)

        session = None
        if refresh_token:
            if expires_at is None:
                lifetime = getattr(
                    settings, "SIMPLE_JWT", {}
                ).get("REFRESH_TOKEN_LIFETIME") or timedelta(days=7)
                expires_at = timezone.now() + lifetime
            session = UserSession.objects.create(
                user=user,
                token=refresh_token[:500],
                ip_address=ip_address,
                user_agent=user_agent or "",
                expires_at=expires_at,
                is_active=True,
            )
        return session

    @staticmethod
    def record_login_failure(
        *,
        username: str = "",
        user: User | None = None,
        ip_address: str | None = None,
        user_agent: str = "",
        reason: str = "Invalid credentials",
    ) -> None:
        if user is None and username:
            user = User.objects.filter(
                username__iexact=username
            ).first()
        if user is None:
            # Cannot attach history without a user FK; skip DB write.
            return
        UserLoginHistory.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent or "",
            success=False,
            failure_reason=(reason or "")[:255],
        )

    @staticmethod
    def deactivate_session_by_token(refresh_token: str) -> None:
        if not refresh_token:
            return
        UserSession.objects.filter(
            token=refresh_token[:500], is_active=True
        ).update(is_active=False)

    @staticmethod
    def revoke_all_sessions(user: User) -> int:
        return UserSession.objects.filter(
            user=user, is_active=True
        ).update(is_active=False)

    @staticmethod
    def list_active_sessions(user: User):
        return UserSession.objects.filter(
            user=user, is_active=True
        ).order_by("-last_activity")

    # --------------------------------------------------
    # Permissions helper (aligned with RolePermission ranks)
    # --------------------------------------------------
    @staticmethod
    def permissions_for_user(user: User) -> list[str]:
        """
        Derive a stable permission string list from role rank so the
        UI stays aligned with RolePermission on ViewSets.
        """
        if user.is_superuser or user.role == UserRole.ADMIN:
            return ["*"]

        rank = ROLE_RANK.get(user.role, -1)
        perms: list[str] = []
        if rank >= ROLE_RANK[UserRole.GUEST]:
            perms.append("view_dashboard")
        if rank >= ROLE_RANK[UserRole.VIEWER]:
            perms.extend(
                ["view_sales", "view_inventory", "view_purchases"]
            )
        if rank >= ROLE_RANK[UserRole.USER]:
            perms.extend(
                ["edit_sales", "edit_inventory", "edit_purchases"]
            )
        if rank >= ROLE_RANK[UserRole.MANAGER]:
            perms.extend(["export_data", "manage_users", "approve"])
        return perms
