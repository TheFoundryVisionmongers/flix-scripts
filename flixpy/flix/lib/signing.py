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
    """
    Sign an HTTP request to the Flix server.

    :param access_key_id: The ID of the access key
    :param secret: The secret part of the access key
    :param method: The HTTP method for the request, e.g. GET or POST
    :param path: The path to request not including the, e.g. /info
    :param body: The body of the request
    :param content_type: The content type of the request
    :return: A dictionary containing headers to send with the request to the Flix server
    """
    date = get_time_rfc3999()

    parts = [method]
    if body:
        parts += [
            hashlib.md5(body.encode("utf-8")).hexdigest(),
            content_type,
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


def signature(msg: bytes, secret: str) -> str:
    """
    Generate a signature for a message using HMAC with SHA256.

    :param msg: The message to sign
    :param secret: The secret to sign the message using
    :return: The signature, encoded with Base64
    """
    return base64.b64encode(hmac.digest(secret.encode(), msg, "sha256")).decode()
