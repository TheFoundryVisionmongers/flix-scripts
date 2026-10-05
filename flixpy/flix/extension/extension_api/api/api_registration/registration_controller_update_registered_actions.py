from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.action_update_request import ActionUpdateRequest
from ...models.actions_update_response import ActionsUpdateResponse
from ...types import UNSET, Response


def _get_kwargs(
    *,
    json_body: ActionUpdateRequest,
) -> Dict[str, Any]:

    cookies = {}

    json_json_body = json_body.to_dict()

    return {
        "method": "post",
        "url": "/registration/actions",
        "json": json_json_body,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[ActionsUpdateResponse, Any]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = ActionsUpdateResponse.from_dict(response.json())

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
) -> Response[Union[ActionsUpdateResponse, Any]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    json_body: ActionUpdateRequest,
) -> Response[Union[ActionsUpdateResponse, Any]]:
    """Update registered actions

     Updates the list of actions that an API client can perform. This is used to keep the Flix Client
    aware of the actions that each
    API client can perform, so that it can send the correct events when those actions are performed by
    the API clients.

    Args:
        json_body (ActionUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ActionsUpdateResponse, Any]]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    json_body: ActionUpdateRequest,
) -> Optional[Union[ActionsUpdateResponse, Any]]:
    """Update registered actions

     Updates the list of actions that an API client can perform. This is used to keep the Flix Client
    aware of the actions that each
    API client can perform, so that it can send the correct events when those actions are performed by
    the API clients.

    Args:
        json_body (ActionUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ActionsUpdateResponse, Any]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    json_body: ActionUpdateRequest,
) -> Response[Union[ActionsUpdateResponse, Any]]:
    """Update registered actions

     Updates the list of actions that an API client can perform. This is used to keep the Flix Client
    aware of the actions that each
    API client can perform, so that it can send the correct events when those actions are performed by
    the API clients.

    Args:
        json_body (ActionUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[ActionsUpdateResponse, Any]]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    json_body: ActionUpdateRequest,
) -> Optional[Union[ActionsUpdateResponse, Any]]:
    """Update registered actions

     Updates the list of actions that an API client can perform. This is used to keep the Flix Client
    aware of the actions that each
    API client can perform, so that it can send the correct events when those actions are performed by
    the API clients.

    Args:
        json_body (ActionUpdateRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[ActionsUpdateResponse, Any]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
