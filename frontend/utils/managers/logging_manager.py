# frontend/utils/logging_config.py

import logging
import logging.handlers
from pathlib import Path

from frontend.utils.config import (
    SESSION_DIR, LOG_DIR, LOG_FILE, INFO_LOG, DEBUG_LOG, 
    WARNING_LOG, CRITICAL_LOG, ERROR_LOG
)


class _ExactLevelFilter(logging.Filter):
    """Only allow records at exactly one level through."""

    def __init__(self, level: int):
        super().__init__()
        self._level = level

    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno == self._level


class LoggingManager:
    """
    Manages application-wide logging configuration.

    Sets up separate rotating log files per level, a combined log,
    and a console handler — all under ~/.storica/logs/.

    Typical usage:

        # In main.py, before any other imports that use logging:
        LoggingManager().setup()

        # Anywhere else in the app:
        logger = logging.getLogger(__name__)
        logger.info("Something happened.")
    """

    _LOG_DIR = Path.home() / SESSION_DIR / LOG_DIR

    _PER_LEVEL_FILES = [
        (DEBUG_LOG   , logging.DEBUG),
        (INFO_LOG    , logging.INFO),
        (WARNING_LOG , logging.WARNING),
        (ERROR_LOG   , logging.ERROR),
        (CRITICAL_LOG, logging.CRITICAL),
    ]

    _SUPPRESSED_LOGGERS = [
        "urllib3",
        "requests",
    ]

    def __init__(
        self,
        level: int = logging.DEBUG,
        max_bytes: int = 5 * 1024 * 1024,
        backup_count: int = 3,
        console_level: int = logging.INFO,
    ):
        """
        Args:
            level        : Root logger level (default DEBUG — captures everything).
            max_bytes    : Max size per log file before rotation (default 5 MB).
            backup_count : Number of rotated backups to keep (default 3).
            console_level: Minimum level printed to terminal (default INFO).
        """
        self._level = level
        self._max_bytes = max_bytes
        self._backup_count = backup_count
        self._console_level = console_level
        self._root = logging.getLogger()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def setup(self) -> None:
        """
        Configure the root logger.

        Safe to call multiple times — subsequent calls are no-ops if
        handlers are already attached.
        """
        if self._root.handlers:
            return

        self._ensure_log_dir()
        self._root.setLevel(self._level)

        file_formatter = self._make_formatter(show_lineno=True)
        console_formatter = self._make_formatter(show_lineno=False, time_fmt="%H:%M:%S")

        for filename, lvl in self._PER_LEVEL_FILES:
            self._root.addHandler(
                self._make_rotating_handler(filename, lvl, file_formatter, exact=True)
            )

        # all.log — every level in one place for full traces.
        self._root.addHandler(
            self._make_rotating_handler(LOG_FILE, logging.DEBUG, file_formatter, exact=False)
        )

        self._root.addHandler(
            self._make_console_handler(console_formatter)
        )

        self._suppress_noisy_loggers()

        logging.debug("LoggingManager: logging initialised. Log dir: %s", self._LOG_DIR)

    def teardown(self) -> None:
        """
        Remove and close all handlers attached to the root logger.

        Useful in tests to reset logging state between runs.
        """
        for handler in self._root.handlers[:]:
            handler.close()
            self._root.removeHandler(handler)

    @property
    def log_dir(self) -> Path:
        """Path to the directory containing all log files."""
        return self._LOG_DIR

    # ------------------------------------------------------------------
    # Private — setup helpers
    # ------------------------------------------------------------------

    def _ensure_log_dir(self) -> None:
        try:
            self._LOG_DIR.mkdir(parents=True, exist_ok=True)
            
        except OSError as exc:
            # Can't raise here — logging isn't up yet. Fall through;
            # file handlers will fail gracefully below.
            print(f"[LoggingManager] Could not create log directory: {exc}")

    def _make_formatter(
        self,
        show_lineno: bool = True,
        time_fmt: str = "%Y-%m-%d %H:%M:%S",
    ) -> logging.Formatter:
        lineno_part = ":%(lineno)d" if show_lineno else ""
        fmt = f"%(asctime)s | %(levelname)-8s | %(name)s{lineno_part} | %(message)s"
        return logging.Formatter(fmt=fmt, datefmt=time_fmt)

    def _make_rotating_handler(
        self,
        filename: str,
        level: int,
        formatter: logging.Formatter,
        exact: bool = True,
    ) -> logging.handlers.RotatingFileHandler:
        handler = logging.handlers.RotatingFileHandler(
            self._LOG_DIR / filename,
            maxBytes=self._max_bytes,
            backupCount=self._backup_count,
            encoding="utf-8",
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)

        if exact:
            handler.addFilter(_ExactLevelFilter(level))

        return handler

    def _make_console_handler(
        self,
        formatter: logging.Formatter,
    ) -> logging.StreamHandler:
        handler = logging.StreamHandler()
        handler.setLevel(self._console_level)
        handler.setFormatter(formatter)
        return handler

    def _suppress_noisy_loggers(self) -> None:
        for name in self._SUPPRESSED_LOGGERS:
            logging.getLogger(name).setLevel(logging.WARNING)