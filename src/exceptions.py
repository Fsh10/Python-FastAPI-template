from typing import Any

from fastapi import HTTPException, status


def exception_handler(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as ex:
            raise InternalServerErrorException(error=ex)

    return wrapper


class InternalServerErrorException(Exception):
    def __init__(self, message="Internal server error"):
        self.message = message
        super().__init__(self.message)


class DefaultException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "Something went wrong",
        error: Any = "",
    ) -> None:
        super().__init__(
            status_code=status_code, detail={"message": message, "error": error}
        )


class InternalServerErrorException(DefaultException):
    def __init__(
        self,
        message: Any = "Server error",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class BadRequestException(DefaultException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        message: Any = "Error sending request",
        error: Any = "",
    ) -> None:
        super().__init__(status_code, message, error)


class NotFoundException(DefaultException):
    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        message: Any = "Not found",
        error: Any = "",
    ) -> None:
        super().__init__(status_code, message, error)


class ConflictException(DefaultException):
    def __init__(
        self,
        status_code: int = status.HTTP_409_CONFLICT,
        message: Any = "Conflict",
        error: Any = "",
    ) -> None:
        super().__init__(status_code, message, error)


class UnprocessableEntityException(DefaultException):
    def __init__(
        self,
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        message: Any = "Unprocessable entity",
        error: Any = "",
    ) -> None:
        super().__init__(status_code, message, error)


class UserNotFoundException(NotFoundException):
    def __init__(
        self,
        message: str = "User does not exist",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class UserHasNotConfirmedException(DefaultException):
    def __init__(
        self,
        status_code=status.HTTP_403_FORBIDDEN,
        message: Any = "User has not confirmed data",
        error: Any = "",
    ) -> None:
        super().__init__(status_code, message, error)


class UserUnauthorizedException(DefaultException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        message: str = "You are not authorized",
        error: Any = "",
    ) -> None:
        super().__init__(status_code, message, error)


class UserBadCredentialsException(BadRequestException):
    def __init__(
        self,
        message: str = "Invalid credentials",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class UserAlreadyExistsException(ConflictException):
    def __init__(
        self,
        message: str = "User already exists",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class ResetPasswordBadTokenException(BadRequestException):
    def __init__(
        self,
        message: Any = "Token expired",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class BadTokenException(BadRequestException):
    def __init__(
        self,
        message: Any = "Invalid token",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class WebsocketDisconnectException(InternalServerErrorException):
    def __init__(
        self,
        message: str = "WebSocket disconnected",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class WebsocketUnexpectedErrorException(InternalServerErrorException):
    def __init__(
        self,
        message: str = "Unexpected WebSocket error",
        error: Any = "",
    ) -> None:
        if "ConnectionClosedError" in str(type(error)) or "ConnectionClosed" in str(
            type(error)
        ):
            error = "WebSocket connection closed"
        super().__init__(message=message, error=error)


class UpdateScriptException(DefaultException):
    def __init__(self, message: str = "Something went wrong", error: Any = "") -> None:
        super().__init__(message=message, error=error)


class InvalidPasswordException(BadRequestException):
    def __init__(
        self,
        message: Any = "Invalid password",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class UnsupportedFileFormatException(UnprocessableEntityException):
    def __init__(
        self,
        message: Any = "Unsupported file format",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class FileNotFoundException(NotFoundException):
    def __init__(
        self,
        message: Any = "File not found at this path",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class UnknownExtensionException(BadRequestException):
    def __init__(
        self,
        message: Any = "Unknown extension",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class FileAlreadyExists(ConflictException):
    def __init__(
        self,
        message: Any = "File already exists",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class UnprocessableEntityException(UnprocessableEntityException):
    def __init__(
        self,
        message: Any = "Unprocessable entity",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class PermissionDeniedException(DefaultException):
    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        message: str = "Insufficient permissions",
        error: Any = "",
    ) -> None:
        super().__init__(status_code=status_code, message=message, error=error)


class LinkExpiredException(DefaultException):
    def __init__(
        self,
        status_code: int = status.HTTP_423_LOCKED,
        message: str = "Link expiration time has ended",
        error: Any = "",
    ) -> None:
        super().__init__(status_code=status_code, message=message, error=error)


class OrganizationAlreadyExistsException(ConflictException):
    def __init__(
        self,
        message: Any = "Organization with this name already exists",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class ErrorWhileRequestDataException(InternalServerErrorException):
    def __init__(
        self,
        message: Any = "Error requesting data",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)


class UserBusyException(BadRequestException):
    def __init__(
        self,
        message: str = "Worker is already busy",
        error: Any = "",
    ) -> None:
        super().__init__(message=message, error=error)
