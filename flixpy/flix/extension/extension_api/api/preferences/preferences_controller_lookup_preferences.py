from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.preferences_controller_lookup_preferences_response_200 import (
    PreferencesControllerLookupPreferencesResponse200,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    keys: Union[Unset, None, List[str]] = UNSET,
) -> Dict[str, Any]:
    pass

    params: Dict[str, Any] = {}
    json_keys: Union[Unset, None, List[str]] = UNSET
    if not isinstance(keys, Unset):
        if keys is None:
            json_keys = None
        else:
            json_keys = keys

    params["keys"] = json_keys

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": "/preferences",
        "params": params,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, PreferencesControllerLookupPreferencesResponse200]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PreferencesControllerLookupPreferencesResponse200.from_dict(
            response.json()
        )

        return response_200
    if response.status_code == HTTPStatus.BAD_REQUEST:
        response_400 = cast(Any, None)
        return response_400
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[Any, PreferencesControllerLookupPreferencesResponse200]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    keys: Union[Unset, None, List[str]] = UNSET,
) -> Response[Union[Any, PreferencesControllerLookupPreferencesResponse200]]:
    """Get Flix Preferences Values

    Args:
        keys (Union[Unset, None, List[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PreferencesControllerLookupPreferencesResponse200]]
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
    keys: Union[Unset, None, List[str]] = UNSET,
) -> Optional[Union[Any, PreferencesControllerLookupPreferencesResponse200]]:
    """Get Flix Preferences Values

    Args:
        keys (Union[Unset, None, List[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PreferencesControllerLookupPreferencesResponse200]
    """

    return sync_detailed(
        client=client,
        keys=keys,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    keys: Union[Unset, None, List[str]] = UNSET,
) -> Response[Union[Any, PreferencesControllerLookupPreferencesResponse200]]:
    """Get Flix Preferences Values

    Args:
        keys (Union[Unset, None, List[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PreferencesControllerLookupPreferencesResponse200]]
    """

    kwargs = _get_kwargs(
        keys=keys,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    keys: Union[Unset, None, List[str]] = UNSET,
) -> Optional[Union[Any, PreferencesControllerLookupPreferencesResponse200]]:
    """Get Flix Preferences Values

    Args:
        keys (Union[Unset, None, List[str]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PreferencesControllerLookupPreferencesResponse200]
    """

    return (
        await asyncio_detailed(
            client=client,
            keys=keys,
        )
    ).parsed
