from http import HTTPStatus
from typing import Any, Dict, List, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.event_controller_handle_connection_event_item import (
    EventControllerHandleConnectionEventItem,
)
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    event: Union[Unset, None, List[EventControllerHandleConnectionEventItem]] = UNSET,
) -> Dict[str, Any]:
    pass

    params: Dict[str, Any] = {}
    json_event: Union[Unset, None, List[str]] = UNSET
    if not isinstance(event, Unset):
        if event is None:
            json_event = None
        else:
            json_event = []
            for event_item_data in event:
                event_item = event_item_data.value

                json_event.append(event_item)

    params["event"] = json_event

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    return {
        "method": "get",
        "url": "/events",
        "params": params,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Any]:
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    event: Union[Unset, None, List[EventControllerHandleConnectionEventItem]] = UNSET,
) -> Response[Any]:
    """Subscribe to events from the Client.

     Provides an alternative to the websocket endpoint for API clients to subscribe to events.
    This endpoint uses Server-Sent Events (SSE) to push events to the client.
    It is designed for API clients that cannot use websockets, such as those running in
    environments where websockets are not supported or practical.

    Args:
        event (Union[Unset, None, List[EventControllerHandleConnectionEventItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        event=event,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    event: Union[Unset, None, List[EventControllerHandleConnectionEventItem]] = UNSET,
) -> Response[Any]:
    """Subscribe to events from the Client.

     Provides an alternative to the websocket endpoint for API clients to subscribe to events.
    This endpoint uses Server-Sent Events (SSE) to push events to the client.
    It is designed for API clients that cannot use websockets, such as those running in
    environments where websockets are not supported or practical.

    Args:
        event (Union[Unset, None, List[EventControllerHandleConnectionEventItem]]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        event=event,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
