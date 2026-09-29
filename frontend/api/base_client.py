"""
Base API client with JWT authentication and request handling.

Design principles:
- All requests go through _request() — one path, one error surface.
- Token refresh is proactive (checks expiry) and reactive (handles 401).
- Callers receive a typed APIResult, never a bare None.
- Network, timeout, and server errors are distinguished — not collapsed.
- Every outbound request is logged for auditability.
"""

import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass

from typing import Any
from urllib.parse import urljoin

import requests
from PyQt6.QtCore import QObject, pyqtSignal

from frontend.utils.config import API_BASE_URL

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Result type — replaces bare dict | None returns
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class APIResult:
    """
    Typed wrapper around an API response.

    Attributes:
        ok       : True when the request succeeded (2xx).
        data     : Parsed JSON body on success, or None.
        status   : HTTP status code (0 = network-level failure).
        error    : Human-readable error description, or None on success.
        not_found: True when status is 404 — "record does not exist".
        invalid  : True when status is 400/422 — caller sent bad data.
        server_error: True when status is 5xx — backend problem.
    """
    ok: bool
    data: Any = None
    status: int = 0
    error: str | None = None

    @property
    def not_found(self) -> bool:
        return self.status == 404

    @property
    def invalid(self) -> bool:
        return self.status in (400, 422)

    @property
    def server_error(self) -> bool:
        return self.status >= 500

    @classmethod
    def success(cls, data: Any = None, status: int = 200) -> "APIResult":
        return cls(ok=True, data=data, status=status)

    @classmethod
    def failure(cls, error: str, status: int = 0) -> "APIResult":
        return cls(ok=False, error=error, status=status)

    def __repr__(self) -> str:
        if self.ok:
            return f"<APIResult ok status={self.status}>"
        return f"<APIResult FAIL status={self.status} error={self.error!r}>"


# ---------------------------------------------------------------------------
# Base client
# ---------------------------------------------------------------------------

# How many seconds before expiry to proactively refresh the token.
_REFRESH_BUFFER_SECONDS = 600

# Seconds to wait before retrying a 5xx response.
_RETRY_DELAY_SECONDS = 1.0

# Number of retries on transient 5xx errors.
_MAX_RETRIES = 1

_EXPIRY_IN_MINUTES = 1430


class APIClient(QObject):
    """Base client for all API communications."""

    # Emitted with a short human-readable message on any API error.
    error_occurred = pyqtSignal(str)

    # Emitted when a network-level connection failure happens.
    connection_error = pyqtSignal(str)

    # Emitted when tokens are expired/invalid and refresh has failed.
    # The UI should listen to this and navigate to the login screen.
    session_expired = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.base_url: str = API_BASE_URL.rstrip("/")
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._token_expiry: datetime | None = None

    # ------------------------------------------------------------------
    # Token management
    # ------------------------------------------------------------------

    def set_tokens(self, access: str, refresh: str, expires_in_minutes: int = 55) -> None:
        """Store JWT tokens and record the expected expiry time."""
        self._access_token = access
        self._refresh_token = refresh
        self._token_expiry = datetime.now() + timedelta(minutes=expires_in_minutes)
        logger.debug("Tokens set; expiry in %d minutes.", expires_in_minutes)

    def clear_tokens(self) -> None:
        """Wipe all token state (called on logout or session expiry)."""
        self._access_token = None
        self._refresh_token = None
        self._token_expiry = None

    @property
    def is_authenticated(self) -> bool:
        """True when an access token is present (regardless of expiry)."""
        return bool(self._access_token)

    def _token_needs_refresh(self) -> bool:
        """
        Return True when the access token is absent or will expire soon.
        A buffer of _REFRESH_BUFFER_SECONDS avoids sending a request with
        a token that expires in flight.
        """
        if not self._access_token or not self._token_expiry:
            return True
        return datetime.now() >= self._token_expiry - timedelta(seconds=_REFRESH_BUFFER_SECONDS)

    def _do_refresh(self) -> bool:
        """
        Exchange the refresh token for a new access token.

        Returns True on success, False on any failure.
        Emits session_expired if the refresh token itself is rejected.
        """
        if not self._refresh_token:
            logger.warning("Token refresh attempted with no refresh token.")
            return False

        logger.debug("Refreshing access token.")

        try:
            response = requests.post(
                f"{self.base_url}/token/refresh/",
                json={"refresh": self._refresh_token},
                timeout=10,
            )

        except requests.exceptions.ConnectionError:
            # Network is down — keep existing tokens; do not expire session.
            logger.warning("Token refresh failed: network unavailable.")
            return False

        except Exception as exc:
            logger.exception("Token refresh failed unexpectedly: %s", exc)
            return False

        if response.status_code == 200:
            data = response.json()
            self.set_tokens(
                data.get("access"), 
                self._refresh_token
            )
            logger.debug("Token refreshed successfully.")
            return True

        # Refresh token rejected — session is truly over.
        logger.info(
            "Refresh token rejected (status %d); emitting session_expired.", 
            response.status_code
        )
        self.clear_tokens()
        self.session_expired.emit()
        return False

    # ------------------------------------------------------------------
    # Core request method
    # ------------------------------------------------------------------

    def _build_url(self, endpoint: str) -> str:
        """Join base URL with an endpoint, handling leading slashes cleanly."""
        return urljoin(self.base_url + "/", endpoint.lstrip("/"))

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
        _retry: bool = True,
    ) -> APIResult:
        """
        Make an authenticated HTTP request with automatic token refresh.

        Args:
            method  : HTTP verb — "GET", "POST", "PUT", "PATCH", "DELETE".
            endpoint: API path, e.g. "/invoices/". Joined with base_url.
            data    : JSON body for POST/PUT/PATCH requests.
            params  : Query string parameters for GET (filters, pagination…).
            _retry  : Internal flag; set False to suppress 5xx retry loop.

        Returns:
            APIResult — always. Never raises; never returns None.
        """
        # Proactive refresh before the request goes out.
        if self._token_needs_refresh() and self._refresh_token:
            self._do_refresh()

        url = self._build_url(endpoint)
        headers = self._build_headers()
        method = method.upper()
        started = time.monotonic()

        try:
            response = requests.request(
                method,
                url,
                json=data,
                params=params,
                headers=headers,
                timeout=10,
            )
            
        except requests.exceptions.ConnectionError as exc:
            msg = "Cannot connect to server. Please check your connection."
            logger.warning("[%s %s] Connection error: %s", method, endpoint, exc)
            self.connection_error.emit(msg)
            return APIResult.failure(msg)

        except requests.exceptions.Timeout:
            msg = "Request timed out. Please try again."
            logger.warning("[%s %s] Timeout.", method, endpoint)
            self.error_occurred.emit(msg)
            return APIResult.failure(msg)

        except Exception as exc:
            msg = f"Unexpected error: {exc}"
            logger.exception("[%s %s] %s", method, endpoint, exc)
            self.error_occurred.emit(msg)
            return APIResult.failure(msg)

        elapsed = (time.monotonic() - started) * 1000
        logger.info(
            "[%s %s] → %d  (%.0f ms)",
            method,
            endpoint,
            response.status_code,
            elapsed,
        )

        # --- 401: token may have expired mid-flight; attempt one refresh ---
        if response.status_code == 401:
            if self._refresh_token and self._do_refresh():
                # Retry with new token — but don't recurse infinitely.
                return self._request(method, endpoint, data=data, params=params, _retry=False)

            # Refresh failed or no refresh token.
            msg = "Session expired. Please log in again."
            self.error_occurred.emit(msg)
            return APIResult.failure(msg, status=401)

        # --- 5xx: transient server errors — one retry after a short wait ---
        if response.status_code >= 500 and _retry:
            logger.warning("[%s %s] Server error %d; retrying in %.1fs.", method, endpoint, response.status_code, _RETRY_DELAY_SECONDS)
            time.sleep(_RETRY_DELAY_SECONDS)
            return self._request(method, endpoint, data=data, params=params, _retry=False)

        # --- 4xx client errors (excluding 401 handled above) ---
        if response.status_code >= 400:
            error_msg = f"API Error {response.status_code}: {response.text[:200]}"
            logger.warning("[%s %s] Client error: %s", method, endpoint, error_msg)
            self.error_occurred.emit(error_msg)
            return APIResult.failure(error_msg, status=response.status_code)

        # --- Success ---
        body = response.json() if response.content else None
        return APIResult.success(data=body, status=response.status_code)

    # ------------------------------------------------------------------
    # Convenience methods
    # ------------------------------------------------------------------

    def get(self, endpoint: str, params: dict | None = None) -> APIResult:
        """GET request. Use `params` for filters, pagination, search."""
        return self._request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: dict) -> APIResult:
        """POST request."""
        return self._request("POST", endpoint, data=data)

    def put(self, endpoint: str, data: dict) -> APIResult:
        """PUT request (full replacement)."""
        return self._request("PUT", endpoint, data=data)

    def patch(self, endpoint: str, data: dict) -> APIResult:
        """PATCH request (partial update)."""
        return self._request("PATCH", endpoint, data=data)

    def delete(self, endpoint: str) -> APIResult:
        """DELETE request."""
        return self._request("DELETE", endpoint)

    def logout(self) -> None:
        """Clear all local session state."""
        self.clear_tokens()

    def health_check(self, timeout: float = 3.0) -> APIResult:
        """
        Lightweight probe of GET /api/health/.

        Does not require authentication. Useful for offline detection
        and the About dialog. Uses a short timeout so the UI stays responsive.
        """
        import requests
        from frontend.utils.config import API_HEALTH_URL

        try:
            response = requests.get(API_HEALTH_URL, timeout=timeout)
            if response.status_code == 200:
                return APIResult.success(data=response.json(), status=200)
            return APIResult.failure(
                f"Backend reported status {response.status_code}",
                status=response.status_code,
            )
        except requests.exceptions.ConnectionError:
            msg = "Cannot connect to server. Please check your connection."
            self.connection_error.emit(msg)
            return APIResult.failure(msg)
        except requests.exceptions.Timeout:
            msg = "Health check timed out."
            return APIResult.failure(msg)
        except Exception as exc:
            return APIResult.failure(str(exc))
