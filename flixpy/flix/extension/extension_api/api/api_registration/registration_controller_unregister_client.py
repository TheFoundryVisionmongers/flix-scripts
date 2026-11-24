from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors




def _get_kwargs(
    *,
    authorization: str,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}
    headers["authorization"] = authorization



    

    

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/registration",
    }


    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Any | None:
    if response.status_code == 204:
        return None

    if response.status_code == 400:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    authorization: str,

) -> Response[Any]:
    """ Unregister API consumer

     Removes the registration for the requesting API consumer.

    Args:
        authorization (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        authorization=authorization,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    authorization: str,

) -> Response[Any]:
    """ Unregister API consumer

     Removes the registration for the requesting API consumer.

    Args:
        authorization (str):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        authorization=authorization,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

