"""
Authentication client for STORICA API.

Responsibilities:
- Login (username/password → tokens).
- Auto-login (saved tokens → proactive refresh → verify).
- Logout (server-side blacklist + local wipe).
- Current user read/update/password-change.
- In-memory user/role cache so the UI doesn't hammer /auth/me/.

All requests go through base_client._request() so error handling,
logging, and token refresh happen in exactly one place.
"""

import logging
from typing import Literal

from .base_client import APIClient, APIResult
from frontend.utils.managers import AuthManager

logger = logging.getLogger(__name__)


class AuthClient(APIClient):
    """Client for authentication and user management."""

    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()

        # Cached user profile — populated after successful login/verify.
        # Invalidated on logout.
        self._current_user: dict | None = None

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def login(self, username: str, password: str, remember: bool = False) -> tuple[bool, str]:
        """
        Authenticate with username + password and store tokens.

        Args:
            username: Account username.
            password: Account password.
            remember: Persist tokens to disk for auto-login next session.

        Returns:
            (True, "Login successful") on success.
            (False, reason) on failure.
        """
        # Use _request() so connection errors emit the right signals.
        result = self.post("/token/", {"username": username, "password": password})

        if not result.ok:
            # 401 from the token endpoint = wrong credentials specifically.
            if result.status == 401:
                return False, "Invalid username or password."
            return False, result.error or "Login failed."

        access = result.data.get("access")
        refresh = result.data.get("refresh")

        if not access or not refresh:
            return False, "Server returned an incomplete token response."

        self.set_tokens(access, refresh)

        if remember:
            self.auth_manager.save_tokens(access, refresh)
            logger.debug("Tokens persisted to disk (remember=True).")

        # Pre-populate user cache so the rest of the app can call
        # get_current_user() without an extra network round-trip.
        self._fetch_and_cache_user()

        return True, "Login successful."

    # ------------------------------------------------------------------
    # Auto-login
    # ------------------------------------------------------------------

    def try_auto_login(self) -> tuple[bool, str]:
        """
        Attempt login using tokens saved from a previous session.

        Strategy:
        1. Load saved tokens.
        2. Load them into memory so _do_refresh() can use the refresh token.
        3. Proactively refresh the access token (it's almost certainly stale).
        4. Verify with the server.
        5. On network failure during verification, keep the session alive
           rather than wiping valid tokens — the user may be offline.

        Returns:
            (True, message) on success.
            (False, reason) on failure.
        """
        access_token, refresh_token = self.auth_manager.load_tokens()

        if not access_token or not refresh_token:
            return False, "No saved session found."

        # Load tokens into memory so the refresh machinery can use them.
        self.set_tokens(access_token, refresh_token)

        # Verify with the server (skip if network was down during refresh).
        verify_result = self.verify_token()

        if verify_result is True:
            self._fetch_and_cache_user()
            return True, "Session restored."

        if verify_result is None:
            # Network error during verify — treat as tentative success so the
            # user isn't unexpectedly logged out in a spotty-connection context.
            logger.info(
                "Auto-login: verify call failed (network); \
                proceeding with cached state."
            )
            return True, "Session restored (offline)."

        # Always attempt a refresh — the saved access token is likely expired.
        refreshed = self._do_refresh()

        if not refreshed:
            # _do_refresh() only returns False for network failure OR a truly
            # rejected refresh token.  If the network is up and it still
            # failed, clear persisted tokens.
            if self._access_token is None:
                # Refresh token was explicitly rejected by the server.
                self.auth_manager.clear_tokens()
                return False, "Saved session has expired. Please log in again."

            # Network was unavailable — keep tokens and let the user try.
            logger.info("Auto-login: network unavailable; using cached tokens.")

        # Server explicitly rejected the token.
        self.auth_manager.save_tokens(
            self._access_token, 
            self._refresh_token
        )
        
        return True, "Refreshed token, Session Restored."

    # ------------------------------------------------------------------
    # Token verification
    # ------------------------------------------------------------------

    def _do_refresh(self) -> bool:
        """Override to persist the new token to disk after a successful refresh."""
        refreshed = super()._do_refresh()
        if refreshed and self._access_token and self._refresh_token:
            saved = self.auth_manager.save_tokens(
                self._access_token, 
                self._refresh_token,
            )

            if not saved:
                logger.warning("Token refreshed in memory but failed to persist to disk.")
                
        return refreshed

    # ------------------------------------------------------------------
    # Token verification
    # ------------------------------------------------------------------

    def verify_token(self) -> bool | None:
        """
        Ask the server whether the current access token is valid.

        Returns:
            True  — server confirmed the token is valid.
            False — server explicitly rejected the token.
            None  — network failure (cannot determine validity).
        """
        result = self.get("/auth/verify/")

        if result.status == 0:
            # status=0 means a network-level failure (set in APIResult.failure).
            return None

        if result.ok and isinstance(result.data, dict):
            return result.data.get("authenticated", False)

        return False

    # ------------------------------------------------------------------
    # Current user
    # ------------------------------------------------------------------

    def get_current_user(self, force_refresh: bool = False) -> dict | None:
        """
        Return current user info, using the in-memory cache by default.

        Args:
            force_refresh: Bypass cache and fetch from server.

        Returns:
            User dict on success, None on failure.
        """
        if self._current_user and not force_refresh:
            return self._current_user

        return self._fetch_and_cache_user()

    def update_current_user(
        self,
        user_data: dict,
        method: Literal["PATCH", "PUT"] = "PATCH",
    ) -> APIResult:
        """
        Update current user fields.

        Args:
            user_data: Fields to update.
            method   : "PATCH" for partial update (default), "PUT" for full replace.

        Returns:
            APIResult — check .ok before using .data.
        """
        result = self._request(method, "/auth/me/update/", data=user_data)
        if result.ok and isinstance(result.data, dict):
            self._current_user = result.data
        return result

    def change_password(
        self,
        old_password: str,
        new_password: str,
        confirm_password: str | None = None,
    ) -> tuple[bool, str]:
        """
        Change the current user's password.

        Returns:
            (True, success_message) or (False, error_message).
        """
        result = self.post("/auth/me/change-password/", {
            "old_password": old_password,
            "new_password": new_password,
            "confirm_password": confirm_password or new_password,
        })

        if result.ok:
            return True, result.data.get("message", "Password changed successfully.")

        if result.invalid and isinstance(result.data, dict):
            # Server returns field-level validation errors.
            old_pw_error = result.data.get("old_password")
            if old_pw_error:
                msg = old_pw_error[0] if isinstance(old_pw_error, list) else old_pw_error
                return False, msg

        return False, result.error or "Failed to change password."


    # ------------------------------------------------------------------
    # Admin user management
    # ------------------------------------------------------------------

    def list_users(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        params: dict = {"page": page, "page_size": page_size}
        if search:
            params["search"] = search
        if role:
            params["role"] = role
        if is_active is not None:
            params["is_active"] = str(is_active).lower()
        if ordering:
            params["ordering"] = ordering
        return self.get("/auth/", params=params)

    def create_user(self, user_data: dict) -> APIResult:
        return self.post("/auth/", user_data)

    def update_user(self, user_id: int, user_data: dict) -> APIResult:
        return self.patch(f"/auth/{user_id}/", user_data)

    def deactivate_user(self, user_id: int) -> APIResult:
        return self.delete(f"/auth/{user_id}/")

    def reset_user_password(self, user_id: int, new_password: str) -> APIResult:
        return self.post(
            f"/auth/{user_id}/reset-password/",
            {
                "new_password": new_password,
                "confirm_password": new_password,
            },
        )

    def revoke_user_sessions(self, user_id: int) -> APIResult:
        return self.post(f"/auth/{user_id}/revoke-sessions/", {})

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------


    def logout(self) -> None:
        """
        Blacklist the refresh token on the server, then wipe all local state.

        Server-side blacklist failure is logged but never prevents local logout —
        the user's session must always be clearable from the client side.
        """
        if self._refresh_token:
            self._blacklist_token_on_server(self._refresh_token)

        # Wipe local state regardless of server outcome.
        super().logout()
        self.auth_manager.clear_tokens()
        self._current_user = None
        logger.info("User logged out; local session cleared.")

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fetch_and_cache_user(self) -> dict | None:
        """Fetch /auth/me/ and store the result in the in-memory cache."""
        result = self.get("/auth/me/")
        if result.ok and isinstance(result.data, dict):
            self._current_user = result.data
            logger.debug("User cache populated (id=%s).", result.data.get("id"))
            return self._current_user

        logger.warning("Could not fetch current user: %s", result.error)
        return None

    def _blacklist_token_on_server(self, refresh_token: str) -> None:
        """
        Ask the server to blacklist the refresh token.

        Uses _request() so the call goes through the standard auth headers
        and error-signalling pipeline.  Failure is logged but not raised —
        see logout() for rationale.
        """
        result = self.post("/auth/logout/", {"refresh": refresh_token})

        if result.ok:
            logger.debug("Refresh token blacklisted on server.")
        else:
            # Not a hard failure — the token will eventually expire naturally.
            logger.warning(
                "Server-side token blacklist failed (status=%d): %s",
                result.status,
                result.error,
            )

