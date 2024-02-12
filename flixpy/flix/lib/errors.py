"""Error classes used by the Flix SDK."""

from __future__ import annotations

import dataclasses

__all__ = ["FlixError", "FlixHTTPError", "FlixNotVerifiedError"]


class FlixError(Exception):
    """A generic Flix error."""


@dataclasses.dataclass
class FlixHTTPError(FlixError):
    """An error resulting from a failed HTTP request."""

    status_code: int
    error_message: str

    def __str__(self) -> str:
        """Get a human-readable representation of the error."""
        return f"Error {self.status_code}: {self.error_message}"


class FlixNotVerifiedError(FlixHTTPError):
    """Raised when a request failed due to not being authenticated.

    This can happen if no access key was set, the access key was expired or invalid,
    or the wrong username or password was provided when attempting to authenticate.
    """
