"""Utilities for signing messages to the Flix Server.

These allow an authenticated user to generate the authorization signature
required to access protected endpoints.
"""

from __future__ import annotations

import base64
import datetime
import hashlib
import hmac

__all__ = ["sign_request", "signature"]

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"


def get_time_rfc3999() -> str:
    """Get the current date and time in the format expected by Flix's signing mechanism."""
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    return utc_now.strftime(DATE_FORMAT)


def sign_request(
    access_key_id: str,
    secret: str,
    method: str,
    path: str,
    body: str | None = None,
    content_type: str | None = None,
) -> dict[str, str]:
    """Sign an HTTP request to the Flix server.

    Args:
        access_key_id: The ID of the access key.
        secret: The secret part of the access key.
        method: The HTTP method for the request, e.g. GET or POST.
        path: The path to request not including the hostname, e.g. /info.
        body: The body of the request.
        content_type: The content type of the request.

    Returns:
        A dictionary containing headers to send with the request to the Flix server.
    """
    date = get_time_rfc3999()

    parts = [method]
    if body:
        parts += [
            hashlib.md5(body.encode("utf-8")).hexdigest(),  # noqa: S324
            content_type or "",
        ]
    else:
        parts += ["", ""]
    parts += [date, path]

    msg = "\n".join(parts)
    sig = signature(msg.encode(), secret)
    return {
        "Authorization": f"FNAUTH {access_key_id}:{sig}",
        "X-Date": date,
    }


def signature(msg: bytes, secret: str, as_hex: bool = False) -> str:
    """Generate a signature for a message using HMAC with SHA256.

    Args:
        msg: The message to sign.
        secret: The secret to sign the message using.
        as_hex: Whether to return the signature hex-encoded instead of Base64-encoded.

    Returns:
        The signature, encoded with Base64 by default.
    """
    sig = hmac.digest(secret.encode(), msg, "sha256")
    if as_hex:
        return sig.hex()
    else:
        return base64.b64encode(sig).decode()
