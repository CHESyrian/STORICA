"""
frontend/services/__init__.py

Central service registry — one place to get any API client.

Usage
-----
# In main.py, after login:
    from frontend.services import Services
    Services.init(auth_client)

# In any screen, widget, or dialog:
    from frontend.services import Services
    result = Services.inventory.list_products()
    result = Services.auth.get_current_user()
    result = Services.sales.list_sales_orders()
    result = Services.purchases.list_suppliers()

Rules
-----
- Services.init() is called ONCE at login / auto-login success.
- Services.reset() is called at logout — wipes all clients.
- Never instantiate AuthClient or any service elsewhere.
- Never pass auth_client as a constructor argument to screens.
"""

from __future__ import annotations

from frontend.api import AuthClient
from .inventory_service import InventoryService
from .purchases_service import PurchasesService
from .sales_service import SalesService
from .general_service import GeneralService


class _Services:
    """
    Holds the single live instance of every API client.

    All clients share the same AuthClient so token state (access token,
    refresh token, expiry) is consistent across the entire application.
    """

    def __init__(self) -> None:
        self._auth: AuthClient | None = None
        self._inventory: InventoryService | None = None
        self._purchases: PurchasesService | None = None
        self._sales: SalesService | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def init(self, auth_client: AuthClient) -> None:
        """
        Initialise all service clients from an authenticated AuthClient.

        Call this once, immediately after a successful login or auto-login,
        before any screen is shown.
        """
        self._auth = auth_client
        self._inventory = InventoryService(auth_client)
        self._purchases = PurchasesService(auth_client)
        self._sales = SalesService(auth_client)
        self._general = GeneralService(auth_client)

    def reset(self) -> None:
        """
        Tear down all clients on logout.

        Call this inside your logout handler, after auth_client.logout().
        After reset(), any screen that tries to use a service will get a
        clear RuntimeError rather than silently using a stale token.
        """
        self._auth = None
        self._inventory = None
        self._purchases = None
        self._sales = None

    # ------------------------------------------------------------------
    # Accessors — raise immediately if init() was not called first
    # ------------------------------------------------------------------

    @property
    def auth(self) -> AuthClient:
        if self._auth is None:
            raise RuntimeError(
                "Services.auth accessed before Services.init() was called. "
                "Call Services.init(auth_client) after login."
            )
        return self._auth

    @property
    def inventory(self) -> InventoryService:
        if self._inventory is None:
            raise RuntimeError(
                "Services.inventory accessed before Services.init() was called."
            )
        return self._inventory

    @property
    def purchases(self) -> PurchasesService:
        if self._purchases is None:
            raise RuntimeError(
                "Services.purchases accessed before Services.init() was called."
            )
        return self._purchases

    @property
    def sales(self) -> SalesService:
        if self._sales is None:
            raise RuntimeError(
                "Services.sales accessed before Services.init() was called."
            )
        return self._sales

    @property
    def general(self) -> GeneralService:
        if self._general is None:
            raise RuntimeError(
                "Services.sales accessed before Services.init() was called."
            )
        return self._general


# The single global instance — import this, not the class.
Services = _Services()

