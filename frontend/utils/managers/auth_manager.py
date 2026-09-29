"""
AuthManager — encrypted local token persistence.

Design principles:
- Tokens are encrypted with a per-machine Fernet key.
- The key file and token file are restricted to the owning user (chmod 600)
  on POSIX systems immediately after creation.
- Writes are atomic (write to a temp file, then rename) so a crash mid-save
  never leaves a corrupt token file.
- Machine-ID binding prevents a copied token file from being used on another
  machine.
- All errors are logged, never printed, and always result in a clean
  (None, None) return rather than a raised exception.
"""

import hashlib
import json
import logging
import os
import socket
import stat
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from frontend.utils.config import SESSION_DIR, TOKEN_FILE, KEY_FILE

logger = logging.getLogger(__name__)

# How long a saved session stays valid on disk.
_SESSION_TTL_DAYS = 7

# octal 0o600 — owner read/write only, no group or world access.
_PRIVATE_MODE = stat.S_IRUSR | stat.S_IWUSR


class AuthManager:
    """
    Manages authentication token persistence with local encrypted storage.

    Typical usage:

        manager = AuthManager()

        # After login:
        manager.save_tokens(access, refresh)

        # On next startup:
        access, refresh = manager.load_tokens()
        if access:
            ...  # attempt auto-login

        # On logout:
        manager.clear_tokens()
    """

    def __init__(self):
        self._app_dir = Path.home() / SESSION_DIR
        self._token_file = self._app_dir / TOKEN_FILE
        self._key_file = self._app_dir / KEY_FILE
        self._cipher: Fernet | None = None
        self._init_storage()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _init_storage(self) -> None:
        """
        Create the storage directory and load (or generate) the Fernet key.

        The directory is created with mode 700; the key file with mode 600.
        On Windows, chmod is a no-op but the directory is still created.
        """
        try:
            self._app_dir.mkdir(parents=True, exist_ok=True)
            _set_private(self._app_dir)

        except OSError as exc:
            logger.error("Cannot create session directory %s: %s", self._app_dir, exc)
            # Leave _cipher as None — save/load will be no-ops.
            return

        try:
            if self._key_file.exists():
                key = self._key_file.read_bytes()
                logger.debug("Encryption key loaded from %s.", self._key_file)

            else:
                key = Fernet.generate_key()
                _atomic_write(self._key_file, key, mode="wb")
                _set_private(self._key_file)
                logger.debug("New encryption key generated at %s.", self._key_file)

            self._cipher = Fernet(key)

        except Exception as exc:
            logger.exception("Failed to initialise encryption key: %s", exc)
            self._cipher = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def save_tokens(self, access_token: str, refresh_token: str) -> bool:
        """
        Encrypt and persist tokens to disk.

        Args:
            access_token : Current JWT access token.
            refresh_token: Current JWT refresh token.

        Returns:
            True on success, False if the write failed.
        """
        if not self._cipher:
            logger.warning("save_tokens: cipher not available; tokens not saved.")
            return False

        payload = {
            "access_token": 
                access_token,
            "refresh_token": 
                refresh_token,
            "machine_id": 
                self._machine_id(),
            "saved_at": 
                datetime.now().isoformat(),
            "expires_at": 
                (datetime.now() + timedelta(days=_SESSION_TTL_DAYS)).isoformat(),
        }

        try:
            encrypted = self._cipher.encrypt(json.dumps(payload).encode())
            _atomic_write(self._token_file, encrypted, mode="wb")
            _set_private(self._token_file)
            logger.debug("Tokens saved to %s.", self._token_file)
            return True

        except Exception as exc:
            logger.exception("Failed to save tokens: %s", exc)
            return False

    def load_tokens(self) -> tuple[str | None, str | None]:
        """
        Decrypt and return persisted tokens if they are still valid.

        Validity checks (any failure → (None, None)):
          - Token file exists and can be decrypted.
          - Machine ID in the file matches this machine.
          - The session has not exceeded SESSION_TTL_DAYS.

        Returns:
            (access_token, refresh_token) on success.
            (None, None) on any failure.
        """
        if not self._cipher or not self._token_file.exists():
            return None, None

        try:
            encrypted = self._token_file.read_bytes()
            decrypted = self._cipher.decrypt(encrypted)
            payload = json.loads(decrypted.decode())

        except InvalidToken:
            # File was encrypted with a different key (key rotated / file tampered).
            logger.warning("Token file could not be decrypted; clearing.")
            self.clear_tokens()
            return None, None

        except Exception as exc:
            logger.exception("Unexpected error loading tokens: %s", exc)
            return None, None

        # Machine-ID binding — reject tokens copied from another machine.
        if payload.get("machine_id") != self._machine_id():
            logger.warning("Machine ID mismatch; rejecting saved tokens.")
            self.clear_tokens()
            return None, None

        # Expiry check.
        try:
            expires_at = datetime.fromisoformat(payload["expires_at"])
            
        except (KeyError, ValueError):
            logger.warning("Token file has no valid expiry; clearing.")
            self.clear_tokens()
            return None, None

        if datetime.now() > expires_at:
            logger.info("Saved session expired at %s; clearing.", expires_at)
            self.clear_tokens()
            return None, None

        access = payload.get("access_token")
        refresh = payload.get("refresh_token")

        if not access or not refresh:
            logger.warning("Token file is missing access or refresh token; clearing.")
            self.clear_tokens()
            return None, None

        logger.debug("Tokens loaded successfully (expires %s).", expires_at.date())
        return access, refresh

    def clear_tokens(self) -> None:
        """
        Delete the token file from disk.

        Safe to call even when no file exists.
        """
        try:
            if self._token_file.exists():
                self._token_file.unlink()
                logger.debug("Token file deleted.")
        except OSError as exc:
            logger.error("Failed to delete token file: %s", exc)

    @property
    def has_saved_session(self) -> bool:
        """
        True if a non-expired, machine-matched token file exists.

        Prefer this over calling load_tokens() just to check — it avoids
        decrypting the file twice on startup.
        """
        access, _ = self.load_tokens()
        return access is not None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _machine_id() -> str:
        """
        Derive a stable, opaque identifier for this machine + user account.

        Uses hostname + username, hashed with SHA-256.  Not cryptographically
        binding, but sufficient to prevent casual token file copying.
        """
        try:
            raw = f"{socket.gethostname()}:{os.getlogin()}"
        except OSError:
            # getlogin() can fail in some container / CI environments.
            raw = f"{socket.gethostname()}:{os.environ.get('USER', 'unknown')}"
        return hashlib.sha256(raw.encode()).hexdigest()


# ------------------------------------------------------------------
# Module-level helpers
# ------------------------------------------------------------------

def _atomic_write(path: Path, data: bytes, mode: str = "wb") -> None:
    """
    Write `data` to `path` atomically using a sibling temp file + rename.

    A crash mid-write leaves the original file untouched.  The rename is
    atomic on POSIX; on Windows it requires the destination to not exist
    (Python 3.3+ handles this via os.replace).
    """
    dir_ = path.parent
    fd, tmp_path = tempfile.mkstemp(dir=dir_)
    try:
        with os.fdopen(fd, mode) as fh:
            fh.write(data)
        os.replace(tmp_path, path)
    except Exception:
        # Clean up the temp file if anything went wrong.
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise


def _set_private(path: Path) -> None:
    """
    Set path permissions to 600 (files) or 700 (directories) on POSIX.
    No-op on Windows where os.chmod has limited effect.
    """
    if os.name == "nt":
        return
    try:
        if path.is_dir():
            path.chmod(stat.S_IRWXU)          # 700
        else:
            path.chmod(_PRIVATE_MODE)          # 600
    except OSError as exc:
        logger.warning("Could not set permissions on %s: %s", path, exc)
