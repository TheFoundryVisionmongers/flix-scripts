from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.preferences_controller_lookup_preferences_response_200 import PreferencesControllerLookupPreferencesResponse200
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    keys: list[str] | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    json_keys: list[str] | Unset = UNSET
    if not isinstance(keys, Unset):
        json_keys = keys


    params["keys"] = json_keys


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/preferences",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Any | PreferencesControllerLookupPreferencesResponse200 | None:
    if response.status_code == 200:
        response_200 = PreferencesControllerLookupPreferencesResponse200.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Response[Any | PreferencesControllerLookupPreferencesResponse200]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    keys: list[str] | Unset = UNSET,

) -> Response[Any | PreferencesControllerLookupPreferencesResponse200]:
    """ Get Flix Preferences Values

    Args:
        keys (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | PreferencesControllerLookupPreferencesResponse200]
     """


    kwargs = _get_kwargs(
        keys=keys,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    keys: list[str] | Unset = UNSET,

) -> Any | PreferencesControllerLookupPreferencesResponse200 | None:
    """ Get Flix Preferences Values

    Args:
        keys (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | PreferencesControllerLookupPreferencesResponse200
     """


    return sync_detailed(
        client=client,
keys=keys,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    keys: list[str] | Unset = UNSET,

) -> Response[Any | PreferencesControllerLookupPreferencesResponse200]:
    """ Get Flix Preferences Values

    Args:
        keys (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | PreferencesControllerLookupPreferencesResponse200]
     """


    kwargs = _get_kwargs(
        keys=keys,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    keys: list[str] | Unset = UNSET,

) -> Any | PreferencesControllerLookupPreferencesResponse200 | None:
    """ Get Flix Preferences Values

    Args:
        keys (list[str] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | PreferencesControllerLookupPreferencesResponse200
     """


    return (await asyncio_detailed(
        client=client,
keys=keys,

    )).parsed
