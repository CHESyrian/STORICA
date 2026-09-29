"""
frontend/api/general_service.py

This client does NOT extend APIClient — it receives the shared AuthClient
and delegates every request through it.
"""

from __future__ import annotations

import logging
from typing import Literal, Any

from frontend.api.auth_client import AuthClient
from frontend.api.base_client import APIResult

logger = logging.getLogger(__name__)


class GeneralService:
    """API client for inventory / product endpoints."""

    def __init__(self, auth_client: AuthClient) -> None:
        self._client = auth_client

    # ------------------------------------------------------------------
    # Get All Records
    # ------------------------------------------------------------------
    def get_all(self, model: str):
        """GET /api/model/ - Retrieve all records."""
        return self._client.get(f"/{model}/all/")

    # ------------------------------------------------------------------
    # Accounting reports
    # ------------------------------------------------------------------
    def trial_balance(self, as_of: str | None = None) -> APIResult:
        params: dict[str, Any] = {}
        if as_of:
            params["as_of"] = as_of
        return self._client.get("/accounting/trial-balance/", params=params)

    def profit_loss(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> APIResult:
        params: dict[str, Any] = {}
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        return self._client.get("/accounting/profit-loss/", params=params)

    def accounting_accounts(self) -> APIResult:
        return self._client.get("/accounting/accounts/")

