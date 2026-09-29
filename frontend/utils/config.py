import os

# API Configuration
# Prefer STORICA_API_BASE_URL env var so deployers / power users can override
# without editing source. Falls back to the local-development default.
API_BASE_URL = os.environ.get(
    "STORICA_API_BASE_URL",
    "http://localhost:8000/api",
).rstrip("/")
API_LOGIN_URL = f"{API_BASE_URL}/token/"
API_REFRESH_URL = f"{API_BASE_URL}/token/refresh/"
API_HEALTH_URL = f"{API_BASE_URL}/health/"


# Application Settings
APP_NAME    = "STORICA"
APP_VERSION = "1.0.0"
ORG_NAME    = "AJADYA Corp"


# Cache Settings
CACHE_TTL_SECONDS = 300  # 5 minutes


# UI / UX Settings
THEME = "dark_modern"
DEFAULT_PAGE_SIZE = 50


# Dirs / Files Settings
SESSION_DIR  = ".storica"
KEY_FILE     = "storica.key"
TOKEN_FILE   = "storica.enc"
LOG_DIR      = "log"
LOG_FILE     = "storica.log"
ERROR_LOG    = "storica_error.log"
DEBUG_LOG    = "storica_debug.log"
INFO_LOG     = "storica_info.log"
WARNING_LOG  = "storica_warning.log"
CRITICAL_LOG = "storica_critical.log"


