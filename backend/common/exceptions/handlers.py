import logging

from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from common.api_response import ApiResponse
from common.exceptions.base import AppException


logger = logging.getLogger("erp")


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler
    """

    request = context.get("request")

    trace_id = getattr(request, "id", None)

    # =====================================================
    # Application Exceptions
    # =====================================================
    if isinstance(exc, AppException):

        logger.warning(
            f"{exc.error_code}: {exc.message}",
            exc_info=True,
        )

        return ApiResponse.error(
            message=exc.message,
            errors=exc.extra,
            error_code=exc.error_code,
            status_code=exc.status_code,
            trace_id=trace_id,
        )

    # =====================================================
    # DRF Exceptions
    # =====================================================
    response = exception_handler(exc, context)

    if response is not None:

        logger.warning(
            f"DRF Exception: {str(exc)}",
            exc_info=True,
        )

        return ApiResponse.error(
            message="Request failed",
            errors=response.data,
            error_code="request_failed",
            status_code=response.status_code,
            trace_id=trace_id,
        )

    # =====================================================
    # Unexpected Exceptions
    # =====================================================
    logger.exception("Unhandled exception")

    message = (
        str(exc)
        if settings.DEBUG
        else "Internal server error"
    )

    return ApiResponse.error(
        message=message,
        error_code="server_error",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        trace_id=trace_id,
    )