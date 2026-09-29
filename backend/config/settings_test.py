"""
Fast test settings for STORICA.

Import production/dev settings, then override the expensive bits:

* MD5 password hasher (PBKDF2 dominates suite time when every test
  creates users via ``create_user``)
* Quiet logging (auth / permission tests intentionally hit 401/403)
* Same PostgreSQL engine as runtime so constraints and locking still
  match production

Usage
-----
  DJANGO_SETTINGS_MODULE=config.settings_test python manage.py test
  python run_tests.py          # uses this module by default
"""

from config.settings import *  # noqa: F401, F403

# ---------------------------------------------------------------------------
# Password hashing — largest single speed win
# ---------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ---------------------------------------------------------------------------
# Logging — suppress expected WARNING/ERROR noise from negative API tests
# ---------------------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {"class": "logging.NullHandler"},
    },
    "root": {
        "handlers": ["null"],
        "level": "CRITICAL",
    },
}

# ---------------------------------------------------------------------------
# Debug / email — avoid accidental side effects during tests
# ---------------------------------------------------------------------------
DEBUG = False
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
