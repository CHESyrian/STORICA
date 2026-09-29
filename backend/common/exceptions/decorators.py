import functools
import logging
import traceback

from django.conf import settings

from common.exceptions.base import AppException


logger = logging.getLogger(__name__)


def service_exception_handler(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)

        except AppException:
            raise

        except Exception as exc:

            logger.exception(
                f"Unhandled service exception in {func.__name__}"
            )

            if settings.DEBUG:
                raise

            raise AppException(
                message="Unexpected service error",
                error_code="service_error",
            ) from exc

    return wrapper