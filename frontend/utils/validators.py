"""
ui/dialogs/validators.py

Small, dependency-free validators shared by the form dialogs.
"""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PHONE_RE = re.compile(r"^[0-9+()\-.\s]{6,20}$")


def is_valid_email(value: str) -> bool:
    """Return True if `value` looks like a well-formed email address."""
    return bool(EMAIL_RE.match(value.strip()))


def is_valid_phone(value: str) -> bool:
    """Return True if `value` looks like a well-formed phone number."""
    return bool(PHONE_RE.match(value.strip()))
