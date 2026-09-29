"""
User / permission tests — basic RolePermission and role hierarchy checks.
"""
from django.test import SimpleTestCase, TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from rest_framework.test import APIRequestFactory

from apps.users.models import UserRole
from common.permissions import (
    ROLE_RANK,
    role_at_least,
    role_in,
    IsAuthenticatedAndActive,
    IsAdminRole,
    IsManagerOrAbove,
    IsUserOrAbove,
    IsViewerOrAbove,
    RolePermission,
)


User = get_user_model()


class RoleHierarchyUnitTests(SimpleTestCase):
    """Pure helpers — no DB required."""

    def test_role_rank_ordering(self):
        self.assertLess(ROLE_RANK[UserRole.GUEST], ROLE_RANK[UserRole.VIEWER])
        self.assertLess(ROLE_RANK[UserRole.VIEWER], ROLE_RANK[UserRole.USER])
        self.assertLess(ROLE_RANK[UserRole.USER], ROLE_RANK[UserRole.MANAGER])
        self.assertLess(ROLE_RANK[UserRole.MANAGER], ROLE_RANK[UserRole.ADMIN])

    def test_role_at_least(self):
        class U:
            def __init__(self, role, is_superuser=False, is_authenticated=True):
                self.role = role
                self.is_superuser = is_superuser
                self.is_authenticated = is_authenticated

        self.assertTrue(role_at_least(U(UserRole.MANAGER), UserRole.USER))
        self.assertTrue(role_at_least(U(UserRole.ADMIN), UserRole.MANAGER))
        self.assertFalse(role_at_least(U(UserRole.VIEWER), UserRole.USER))
        self.assertFalse(role_at_least(U(UserRole.GUEST), UserRole.VIEWER))

    def test_role_in_admin_always_allowed(self):
        class U:
            def __init__(self, role, is_superuser=False, is_authenticated=True):
                self.role = role
                self.is_superuser = is_superuser
                self.is_authenticated = is_authenticated

        self.assertTrue(role_in(U(UserRole.ADMIN), (UserRole.VIEWER,)))
        self.assertTrue(role_in(U(UserRole.USER, is_superuser=True), ()))


class PermissionClassTests(TestCase):
    """Permission classes with real User instances and RequestFactory."""

    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create_user(
            username="perm_admin",
            password="x",
            role=UserRole.ADMIN,
            is_staff=True,
        )
        self.manager = User.objects.create_user(
            username="perm_manager",
            password="x",
            role=UserRole.MANAGER,
        )
        self.user = User.objects.create_user(
            username="perm_user",
            password="x",
            role=UserRole.USER,
        )
        self.viewer = User.objects.create_user(
            username="perm_viewer",
            password="x",
            role=UserRole.VIEWER,
        )
        self.guest = User.objects.create_user(
            username="perm_guest",
            password="x",
            role=UserRole.GUEST,
        )
        self.inactive = User.objects.create_user(
            username="perm_inactive",
            password="x",
            role=UserRole.USER,
            is_active=False,
        )

    def _request(self, method, user, path="/api/test/"):
        req = getattr(self.factory, method.lower())(path)
        req.user = user
        return req

    def _view(self, action="list", **role_overrides):
        class V:
            pass

        v = V()
        v.action = action
        for key, val in role_overrides.items():
            setattr(v, key, val)
        return v

    # ------------------------------------------------------------------
    # IsAuthenticatedAndActive
    # ------------------------------------------------------------------
    def test_authenticated_and_active(self):
        perm = IsAuthenticatedAndActive()
        self.assertTrue(
            perm.has_permission(self._request("get", self.user), self._view())
        )
        self.assertFalse(
            perm.has_permission(self._request("get", self.inactive), self._view())
        )
        anon = self._request("get", AnonymousUser())
        self.assertFalse(perm.has_permission(anon, self._view()))

    # ------------------------------------------------------------------
    # Role shortcuts
    # ------------------------------------------------------------------
    def test_is_admin_role(self):
        perm = IsAdminRole()
        self.assertTrue(
            perm.has_permission(self._request("get", self.admin), self._view())
        )
        self.assertFalse(
            perm.has_permission(self._request("get", self.manager), self._view())
        )

    def test_is_manager_or_above(self):
        perm = IsManagerOrAbove()
        self.assertTrue(
            perm.has_permission(self._request("get", self.manager), self._view())
        )
        self.assertTrue(
            perm.has_permission(self._request("get", self.admin), self._view())
        )
        self.assertFalse(
            perm.has_permission(self._request("get", self.user), self._view())
        )

    def test_is_user_or_above(self):
        perm = IsUserOrAbove()
        self.assertTrue(
            perm.has_permission(self._request("get", self.user), self._view())
        )
        self.assertFalse(
            perm.has_permission(self._request("get", self.viewer), self._view())
        )

    def test_is_viewer_or_above(self):
        perm = IsViewerOrAbove()
        self.assertTrue(
            perm.has_permission(self._request("get", self.viewer), self._view())
        )
        self.assertFalse(
            perm.has_permission(self._request("get", self.guest), self._view())
        )

    # ------------------------------------------------------------------
    # RolePermission — action-aware
    # ------------------------------------------------------------------
    def test_role_permission_read_allows_viewer(self):
        perm = RolePermission()
        view = self._view(action="list")
        self.assertTrue(
            perm.has_permission(self._request("get", self.viewer), view)
        )
        self.assertFalse(
            perm.has_permission(self._request("get", self.guest), view)
        )

    def test_role_permission_write_requires_user(self):
        perm = RolePermission()
        view = self._view(action="create")
        self.assertTrue(
            perm.has_permission(self._request("post", self.user), view)
        )
        self.assertFalse(
            perm.has_permission(self._request("post", self.viewer), view)
        )

    def test_role_permission_delete_requires_manager(self):
        perm = RolePermission()
        view = self._view(action="destroy")
        self.assertTrue(
            perm.has_permission(self._request("delete", self.manager), view)
        )
        self.assertFalse(
            perm.has_permission(self._request("delete", self.user), view)
        )

    def test_role_permission_cancel_uses_approve_roles(self):
        perm = RolePermission()
        view = self._view(action="cancel")
        self.assertTrue(
            perm.has_permission(self._request("post", self.manager), view)
        )
        self.assertFalse(
            perm.has_permission(self._request("post", self.user), view)
        )

    def test_role_permission_admin_bypasses(self):
        perm = RolePermission()
        view = self._view(action="destroy")
        self.assertTrue(
            perm.has_permission(self._request("delete", self.admin), view)
        )

    def test_role_permission_inactive_denied(self):
        perm = RolePermission()
        view = self._view(action="list")
        self.assertFalse(
            perm.has_permission(self._request("get", self.inactive), view)
        )

    def test_role_permission_custom_write_roles(self):
        perm = RolePermission()
        # Restrict write to manager+ only
        view = self._view(
            action="create",
            write_roles=(UserRole.MANAGER, UserRole.ADMIN),
        )
        self.assertFalse(
            perm.has_permission(self._request("post", self.user), view)
        )
        self.assertTrue(
            perm.has_permission(self._request("post", self.manager), view)
        )


# =====================================================================
# Auth API + UserService tests
# =====================================================================
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import UserLoginHistory, UserSession
from apps.users.services import UserService


class UserServiceTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username="admin_svc",
            password="password123",
            role=UserRole.ADMIN,
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="user_svc",
            password="password123",
            role=UserRole.USER,
        )

    def test_create_user_admin_ok(self):
        u = UserService.create_user(
            username="newuser",
            password="password123",
            role=UserRole.USER,
            actor=self.admin,
        )
        self.assertEqual(u.username, "newuser")
        self.assertTrue(u.check_password("password123"))

    def test_create_admin_requires_admin_actor(self):
        with self.assertRaises(Exception):
            UserService.create_user(
                username="evil",
                password="password123",
                role=UserRole.ADMIN,
                actor=self.user,
            )

    def test_permissions_for_roles(self):
        self.assertEqual(
            UserService.permissions_for_user(self.admin), ["*"]
        )
        perms = UserService.permissions_for_user(self.user)
        self.assertIn("edit_sales", perms)
        self.assertNotIn("manage_users", perms)

    def test_record_login_success_creates_history_and_session(self):
        session = UserService.record_login_success(
            self.user,
            ip_address="127.0.0.1",
            user_agent="test-agent",
            refresh_token="refresh-token-value-abc",
        )
        self.assertIsNotNone(session)
        self.assertEqual(
            UserLoginHistory.objects.filter(
                user=self.user, success=True
            ).count(),
            1,
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.last_login_ip, "127.0.0.1")

    def test_lockout_after_failures(self):
        for _ in range(5):
            UserService.record_login_failure(
                user=self.user, reason="bad"
            )
        self.assertTrue(UserService.is_locked_out(self.user.username))

    def test_change_password(self):
        UserService.change_password(
            self.user, "password123", "newpassword99"
        )
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword99"))

    def test_admin_reset_revokes_sessions(self):
        UserService.record_login_success(
            self.user,
            refresh_token="tok-1",
        )
        UserService.admin_reset_password(
            self.user.pk, "resetpass99", actor=self.admin
        )
        self.assertFalse(
            UserSession.objects.filter(
                user=self.user, is_active=True
            ).exists()
        )


class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username="admin_api",
            password="password123",
            role=UserRole.ADMIN,
            is_staff=True,
        )
        self.user = User.objects.create_user(
            username="user_api",
            password="password123",
            role=UserRole.USER,
        )

    def _auth(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )
        return refresh

    def test_token_login_records_history(self):
        res = self.client.post(
            "/api/token/",
            {"username": "user_api", "password": "password123"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("access", res.data)
        self.assertTrue(
            UserLoginHistory.objects.filter(
                user=self.user, success=True
            ).exists()
        )

    def test_token_login_failure_recorded(self):
        res = self.client.post(
            "/api/token/",
            {"username": "user_api", "password": "wrong"},
            format="json",
        )
        self.assertEqual(res.status_code, 401)
        self.assertTrue(
            UserLoginHistory.objects.filter(
                user=self.user, success=False
            ).exists()
        )

    def test_me_requires_auth(self):
        res = self.client.get("/api/auth/me/")
        self.assertIn(res.status_code, (401, 403))

    def test_me_returns_profile(self):
        self._auth(self.user)
        res = self.client.get("/api/auth/me/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["username"], "user_api")
        self.assertIn("permissions", res.data)

    def test_list_users_admin_only(self):
        self._auth(self.user)
        res = self.client.get("/api/auth/")
        self.assertEqual(res.status_code, 403)
        self._auth(self.admin)
        res = self.client.get("/api/auth/")
        self.assertEqual(res.status_code, 200)

    def test_create_user_as_admin(self):
        self._auth(self.admin)
        res = self.client.post(
            "/api/auth/",
            {
                "username": "created1",
                "password": "password123",
                "confirm_password": "password123",
                "role": "user",
                "email": "c1@example.com",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 201)
        self.assertTrue(
            User.objects.filter(username="created1").exists()
        )

    def test_change_password(self):
        self._auth(self.user)
        res = self.client.post(
            "/api/auth/me/change-password/",
            {
                "old_password": "password123",
                "new_password": "newpassword99",
                "confirm_password": "newpassword99",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword99"))

    def test_change_password_wrong_old(self):
        self._auth(self.user)
        res = self.client.post(
            "/api/auth/me/change-password/",
            {
                "old_password": "nope",
                "new_password": "newpassword99",
                "confirm_password": "newpassword99",
            },
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_logout_blacklists(self):
        refresh = self._auth(self.user)
        res = self.client.post(
            "/api/auth/logout/",
            {"refresh": str(refresh)},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.data.get("success"))
