"""
Role-based DRF permissions for STORICA.

Roles (from apps.users.models.UserRole):
  admin   – full access (also is_superuser / is_staff)
  manager – read + write + approve + limited user mgmt
  user    – read + write on operational data
  viewer  – read only
  guest   – minimal (authenticated but almost no data access)

Usage on a ViewSet:

    from common.permissions import IsAuthenticatedAndActive, RolePermission

    class ProductViewSet(ModelViewSet):
        permission_classes = [IsAuthenticatedAndActive, RolePermission]
        # optional overrides:
        # read_roles  = (...)   # defaults: viewer and above
        # write_roles = (...)   # defaults: user and above
        # delete_roles = (...)  # defaults: manager and above
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS

from apps.users.models import UserRole


# ------------------------------------------------------------------
# Role hierarchy helpers
# ------------------------------------------------------------------

# Ordered from least to most privileged for comparisons
ROLE_RANK = {
    UserRole.GUEST: 0,
    UserRole.VIEWER: 1,
    UserRole.USER: 2,
    UserRole.MANAGER: 3,
    UserRole.ADMIN: 4,
}

DEFAULT_READ_ROLES = (
    UserRole.VIEWER,
    UserRole.USER,
    UserRole.MANAGER,
    UserRole.ADMIN,
)

DEFAULT_WRITE_ROLES = (
    UserRole.USER,
    UserRole.MANAGER,
    UserRole.ADMIN,
)

DEFAULT_DELETE_ROLES = (
    UserRole.MANAGER,
    UserRole.ADMIN,
)

DEFAULT_APPROVE_ROLES = (
    UserRole.MANAGER,
    UserRole.ADMIN,
)


def _user_role(user) -> str | None:
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserRole.ADMIN
    return getattr(user, "role", None)


def role_at_least(user, minimum_role: str) -> bool:
    """Return True if user's role rank >= minimum_role rank."""
    role = _user_role(user)
    if role is None:
        return False
    return ROLE_RANK.get(role, -1) >= ROLE_RANK.get(minimum_role, 99)


def role_in(user, allowed_roles: tuple | list) -> bool:
    role = _user_role(user)
    if role is None:
        return False
    if role == UserRole.ADMIN or (user and user.is_superuser):
        return True
    return role in allowed_roles


# ------------------------------------------------------------------
# Permission classes
# ------------------------------------------------------------------

class IsAuthenticatedAndActive(BasePermission):
    """User must be authenticated and is_active=True."""

    message = "Authentication required and account must be active."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and getattr(user, "is_active", False)
        )


class IsAdminRole(BasePermission):
    """Only admin / superuser."""

    message = "Administrator role required."

    def has_permission(self, request, view):
        return role_in(request.user, (UserRole.ADMIN,))


class IsManagerOrAbove(BasePermission):
    """Manager or admin."""

    message = "Manager or administrator role required."

    def has_permission(self, request, view):
        return role_at_least(request.user, UserRole.MANAGER)


class IsUserOrAbove(BasePermission):
    """Operational user, manager, or admin (can write)."""

    message = "User role or higher required."

    def has_permission(self, request, view):
        return role_at_least(request.user, UserRole.USER)


class IsViewerOrAbove(BasePermission):
    """Anyone who can at least read data."""

    message = "Viewer role or higher required."

    def has_permission(self, request, view):
        return role_at_least(request.user, UserRole.VIEWER)


class RolePermission(BasePermission):
    """
    Action-aware role permission.

    ViewSets can override class attributes:
      read_roles, write_roles, delete_roles, approve_roles

    Mapping:
      SAFE_METHODS / list / retrieve          → read_roles
      create / update / partial_update        → write_roles
      destroy                                 → delete_roles
      custom actions named approve_* / complete_* → approve_roles
      other custom actions                    → write_roles
    """

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if not getattr(user, "is_active", False):
            return False
        if user.is_superuser or _user_role(user) == UserRole.ADMIN:
            return True

        action = getattr(view, "action", None)
        read_roles = getattr(view, "read_roles", DEFAULT_READ_ROLES)
        write_roles = getattr(view, "write_roles", DEFAULT_WRITE_ROLES)
        delete_roles = getattr(view, "delete_roles", DEFAULT_DELETE_ROLES)
        approve_roles = getattr(view, "approve_roles", DEFAULT_APPROVE_ROLES)

        if request.method in SAFE_METHODS or action in ("list", "retrieve"):
            return role_in(user, read_roles)

        if action == "destroy":
            return role_in(user, delete_roles)

        if action and (
            action.startswith("approve")
            or action.startswith("complete")
            or action.startswith("cancel")
        ):
            return role_in(user, approve_roles)

        # create / update / partial_update / other writes
        return role_in(user, write_roles)


class ReadOnly(BasePermission):
    """Allow only safe methods (combine with other classes)."""

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
