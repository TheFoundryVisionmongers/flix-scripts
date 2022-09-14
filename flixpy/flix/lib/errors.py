import dataclasses


__all__ = ["FlixError", "FlixNotVerifiedError"]


@dataclasses.dataclass
class FlixError(OSError):
    """A generic Flix error."""

    status_code: int
    error_message: str

    def __str__(self) -> str:
        return f"Error {self.status_code}: {self.error_message}"


class FlixNotVerifiedError(FlixError):
    """Raised when a request failed due to not being authenticated.

    This can happen if no access key was set, the access key was expired or invalid,
    or the wrong username or password was provided when attempting to authenticate."""

    pass
