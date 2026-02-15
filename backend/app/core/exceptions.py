from fastapi import HTTPException, status


class FilmMatchError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(FilmMatchError):
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            status_code=404,
        )


class AuthenticationError(FilmMatchError):
    def __init__(self, message: str = "Invalid or expired credentials"):
        super().__init__(message=message, status_code=401)


class RateLimitError(FilmMatchError):
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(
            message=f"Rate limit exceeded. Retry after {retry_after} seconds.",
            status_code=429,
        )


class ExternalServiceError(FilmMatchError):
    def __init__(self, service: str, detail: str = ""):
        super().__init__(
            message=f"External service error ({service}): {detail}",
            status_code=502,
        )


def credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
