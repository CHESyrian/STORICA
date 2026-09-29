#!/usr/bin/env python3
"""
STORICA — Professional POS Desktop Application
Main entry point.

Auth + service lifecycle:
  1. Startup  → try_auto_login() → Services.init(auth_client)
  2. Login    → LoginDialog      → Services.init(auth_client)
  3. Logout   → MainWindow close → Services.reset()
  4. session_expired signal      → Services.reset() → login loop
"""

import logging
import sys

from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtGui import QFont

from frontend.ui import LoginDialog, MainWindow
from frontend.utils.config import APP_NAME, ORG_NAME, THEME
from frontend.utils.managers import (
    MessageManager, ThemeManager, LoggingManager
)
from frontend.utils.constants import FontFamily, FontSize
from frontend.api import AuthClient
from frontend.services import Services

LoggingManager().setup()

logger = logging.getLogger(__name__)



# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _apply_theme(app: QApplication, theme_manager: ThemeManager) -> None:
    if not theme_manager.apply_theme(app, THEME):
        logger.warning("Could not load theme '%s'; using Qt default.", THEME)


def _wire_signals(auth_client: AuthClient, message_manager: MessageManager) -> None:
    """
    Connect AuthClient signals to app-level handlers.
    Called once per AuthClient instance before any network call.
    """
    auth_client.error_occurred.connect(
        lambda msg: message_manager.error("API Error", msg)
    )
    auth_client.connection_error.connect(
        lambda msg: message_manager.warning("Connection Error", msg)
    )


def _try_auto_login(message_manager: MessageManager) -> AuthClient | None:
    """
    Silently restore a previous session.
    Returns a ready AuthClient and calls Services.init() on success.
    """
    auth_client = AuthClient()
    _wire_signals(auth_client, message_manager)

    try:
        ok, message = auth_client.try_auto_login()
        
        if ok:
            logger.info("Auto-login succeeded: %s", message)
            Services.init(auth_client)
            return auth_client
        logger.info("Auto-login skipped: %s", message)

    except Exception:
        logger.exception("Unexpected error during auto-login.")
        message_manager.error(
            "Session Error",
            "Could not restore your previous session. Please log in again.",
        )

    return None


def _run_login_loop(
    app: QApplication,
    message_manager: MessageManager,
) -> AuthClient | None:
    """
    Show LoginDialog until the user logs in or closes it.
    Calls Services.init() on success.
    """
    while True:
        dialog = LoginDialog()

        if dialog.exec() != QDialog.DialogCode.Accepted:
            logger.info("Login cancelled.")
            return None

        auth_client: AuthClient = dialog.auth_client
        _wire_signals(auth_client, message_manager)

        verified = auth_client.verify_token()

        if verified is True:
            Services.init(auth_client)           # register all clients
            return auth_client

        if verified is None:
            # Network down between login and verify — proceed cautiously.
            logger.warning("Token verify failed (network); proceeding offline.")
            Services.init(auth_client)
            return auth_client

        # Explicitly rejected — loop back to dialog.
        logger.warning("Token invalid after login; re-showing dialog.")
        message_manager.warning(
            "Session Expired",
            "Your session expired immediately after login. Please try again.",
        )
        auth_client.logout()


def _run_main_window(auth_client: AuthClient) -> bool:
    """
    Show MainWindow and block until it closes.

    Returns True  — user logged out   → re-enter login loop.
    Returns False — window closed     → exit the app.

    session_expired closes the window AND resets Services so any
    in-flight screen gets a clean RuntimeError, not a stale token.
    """
    main_window = MainWindow(auth_client)

    def _on_session_expired() -> None:
        logger.info("Session expired mid-session; closing main window.")
        Services.reset()                         # tear down all clients
        main_window.close()

    auth_client.session_expired.connect(_on_session_expired)
    main_window.show()

    QApplication.instance().exec()

    logged_out = not auth_client.is_authenticated
    if logged_out:
        Services.reset()                         # tear down on explicit logout
    return logged_out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    app.setFont(QFont(FontFamily.SEGOE, FontSize.FONT_SIZE_10))

    _apply_theme(app, ThemeManager())

    message_manager = MessageManager()

    # 1 — Silent session restore
    auth_client = _try_auto_login(message_manager)
    if auth_client:
        logged_out = _run_main_window(auth_client)
        if not logged_out:
            sys.exit(0)

    # 2 — Login loop (first run, or after logout / session expiry)
    while True:
        auth_client = _run_login_loop(app, message_manager)
        if auth_client is None:
            break                                # user closed dialog → exit

        logged_out = _run_main_window(auth_client)
        if not logged_out:
            break                                # window closed → exit
        # logged out → loop back to login dialog

    sys.exit(0)


if __name__ == "__main__":
    main()


# ===========================================================================
# HOW ANY SCREEN MAKES API CALLS — no auth_client argument needed
# ===========================================================================
#
# frontend/ui/inventory/product_list.py
#
# from PyQt6.QtWidgets import QWidget
# from frontend.services import Services
#
#
# class ProductListWidget(QWidget):
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self._load()
#
#     def _load(self):
#         result = Services.inventory.list_products(
#             search="bolt",
#             in_stock=True,
#             page=1,
#         )
#         if result.ok:
#             self._populate_table(result.data["results"])
#         elif result.not_found:
#             self._show_empty_state()
#         elif result.server_error:
#             self._show_error("Server unavailable. Try again shortly.")
#         else:
#             self._show_error(result.error)
#
#     def _on_save(self):
#         result = Services.inventory.create_product({
#             "name": "M8 Bolt",
#             "sku": "BOLT-M8-50",
#             "price": "0.45",
#             "stock_qty": 500,
#         })
#         if result.ok:
#             self._load()
#         elif result.invalid:
#             self._show_field_errors(result.data)   # DRF field-level errors
#         else:
#             self._show_error(result.error)
#
#     def _on_adjust_stock(self, product_id: int):
#         result = Services.inventory.adjust_stock(
#             product_id=product_id,
#             quantity_delta=-5,
#             reason="damaged",
#         )
#         if result.ok:
#             self._load()