"""UserController — admin user management + profile actions."""

from __future__ import annotations

import logging
from typing import Any

from frontend.services import Services
from frontend.api import APIResult

logger = logging.getLogger(__name__)


class UserController:

    def __init__(self) -> None:
        self._auth = None

    @property
    def auth(self):
        if self._auth is None:
            self._auth = Services.auth
        return self._auth

    def load_users(
        self,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        role: str | None = None,
        is_active: bool | None = None,
        ordering: str | None = None,
    ) -> APIResult:
        result = self.auth.list_users(
            page=page,
            page_size=page_size,
            search=search,
            role=role,
            is_active=is_active,
            ordering=ordering,
        )
        if not result.ok:
            logger.warning("Failed to load users: %s", result.error)
        return result

    def create_user(self, data: dict[str, Any]) -> APIResult:
        result = self.auth.create_user(data)
        if result.ok:
            logger.debug("User created: %s", result.data)
        else:
            logger.warning("Create user failed: %s", result.error)
        return result

    def update_user(self, user_id: int, data: dict[str, Any]) -> APIResult:
        return self.auth.update_user(user_id, data)

    def deactivate_user(self, user_id: int) -> APIResult:
        return self.auth.deactivate_user(user_id)

    def reset_password(self, user_id: int, new_password: str) -> APIResult:
        return self.auth.reset_user_password(user_id, new_password)

    def revoke_sessions(self, user_id: int) -> APIResult:
        return self.auth.revoke_user_sessions(user_id)

    def update_profile(self, data: dict[str, Any]) -> APIResult:
        return self.auth.update_current_user(data)

    def change_password(
        self, old_password: str, new_password: str, confirm: str
    ) -> tuple[bool, str]:
        return self.auth.change_password(
            old_password, new_password, confirm_password=confirm
        )
