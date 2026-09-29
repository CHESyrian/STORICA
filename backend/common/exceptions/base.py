from rest_framework import status


class AppException(Exception):

    default_message = "Application error"
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_error_code = "application_error"

    def __init__(
        self,
        message=None,
        extra=None,
        status_code=None,
        error_code=None,
    ):
        self.message = message or self.default_message

        self.extra = extra or {}

        self.status_code = (
            status_code
            or self.default_status_code
        )

        self.error_code = (
            error_code
            or self.default_error_code
        )

        super().__init__(self.message)


class ValidationException(AppException):

    default_message = "Validation failed"
    default_status_code = status.HTTP_400_BAD_REQUEST
    default_error_code = "validation_error"


class BusinessLogicException(AppException):

    default_message = "Business rule violation"
    default_status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_error_code = "business_error"


class NotFoundException(AppException):

    default_message = "Resource not found"
    default_status_code = status.HTTP_404_NOT_FOUND
    default_error_code = "not_found"


class PermissionDeniedException(AppException):

    default_message = "Permission denied"
    default_status_code = status.HTTP_403_FORBIDDEN
    default_error_code = "permission_denied"


class AuthenticationException(AppException):

    default_message = "Authentication failed"
    default_status_code = status.HTTP_401_UNAUTHORIZED
    default_error_code = "authentication_failed"


class ConflictException(AppException):

    default_message = "Resource conflict"
    default_status_code = status.HTTP_409_CONFLICT
    default_error_code = "conflict"