import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =========================================================
# LOG DIRECTORY
# =========================================================

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

DEBUG = os.getenv("DEBUG", "True") == "True"

# =========================================================
# LOGGING CONFIG
# =========================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    # =====================================================
    # FORMATTERS
    # =====================================================
    "formatters": {

        # Production formatter
        "standard": {
            "format": (
                "[{levelname}] "
                "{asctime} "
                "{name} "
                "{module}:{lineno} "
                "{message}"
            ),
            "style": "{",
        },

        # Lightweight console formatter
        "simple": {
            "format": (
                "[{levelname}] "
                "{message}"
            ),
            "style": "{",
        },
    },

    # =====================================================
    # HANDLERS
    # =====================================================
    "handlers": {

        # -------------------------------------------------
        # Console
        # -------------------------------------------------
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard" if DEBUG else "simple",
            "level": "DEBUG" if DEBUG else "INFO",
        },

        # -------------------------------------------------
        # Main Project Log
        # -------------------------------------------------
        "file": {
            "class": (
                "logging.handlers.TimedRotatingFileHandler"
            ),

            "filename": str(
                LOG_DIR / "project.log"
            ),

            "when": "midnight",

            "interval": 1,

            "backupCount": 30,

            "encoding": "utf-8",

            "formatter": "standard",

            "level": "INFO",
        },

        # -------------------------------------------------
        # Error Log
        # -------------------------------------------------
        "error_file": {
            "class": (
                "logging.handlers.TimedRotatingFileHandler"
            ),

            "filename": str(
                LOG_DIR / "errors.log"
            ),

            "when": "midnight",

            "interval": 1,

            "backupCount": 60,

            "encoding": "utf-8",

            "formatter": "standard",

            "level": "ERROR",
        },

        # -------------------------------------------------
        # Security Log
        # -------------------------------------------------
        "security_file": {
            "class": (
                "logging.handlers.TimedRotatingFileHandler"
            ),

            "filename": str(
                LOG_DIR / "security.log"
            ),

            "when": "midnight",

            "interval": 1,

            "backupCount": 90,

            "encoding": "utf-8",

            "formatter": "standard",

            "level": "WARNING",
        },
    },

    # =====================================================
    # LOGGERS
    # =====================================================
    "loggers": {

        # -------------------------------------------------
        # Django Core
        # -------------------------------------------------
        "django": {
            "handlers": [
                "console",
                "file",
                "error_file",
            ],

            "level": "INFO",

            "propagate": True,
        },

        # -------------------------------------------------
        # Your Apps
        # Example:
        # apps.orders.services
        # apps.inventory.views
        # -------------------------------------------------
        "apps": {
            "handlers": [
                "console",
                "file",
                "error_file",
            ],

            "level": (
                "DEBUG" if DEBUG else "INFO"
            ),

            "propagate": False,
        },

        # -------------------------------------------------
        # Security Events
        # -------------------------------------------------
        "security": {
            "handlers": [
                "console",
                "security_file",
            ],

            "level": "WARNING",

            "propagate": False,
        },

        # -------------------------------------------------
        # SQL Queries
        # Enable DEBUG temporarily when needed
        # -------------------------------------------------
        "django.db.backends": {
            "handlers": [
                "console",
            ],

            "level": "WARNING",

            "propagate": False,
        },
    },

    # =====================================================
    # ROOT LOGGER
    # =====================================================
    "root": {
        "handlers": [
            "console",
            "file",
            "error_file",
        ],

        "level": "INFO",
    },
}