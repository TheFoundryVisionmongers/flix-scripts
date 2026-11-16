from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.event_controller_handle_connection_event_item import EventControllerHandleConnectionEventItem
from ...models.sse_event import SSEEvent
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    event: list[EventControllerHandleConnectionEventItem] | Unset = UNSET,

) -> dict[str, Any]:
    

    

    params: dict[str, Any] = {}

    json_event: list[str] | Unset = UNSET
    if not isinstance(event, Unset):
        json_event = []
        for event_item_data in event:
            event_item = event_item_data.value
            json_event.append(event_item)


    params["event"] = json_event


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/events",
        "params": params,
    }


    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> SSEEvent | None:
    if response.status_code == 200:
        response_200 = SSEEvent.from_dict(response.text)



        return response_200

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Response[SSEEvent]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    event: list[EventControllerHandleConnectionEventItem] | Unset = UNSET,

) -> Response[SSEEvent]:
    """ Subscribe to events from the Client.

    Args:
        event (list[EventControllerHandleConnectionEventItem] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SSEEvent]
     """


    kwargs = _get_kwargs(
        event=event,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    event: list[EventControllerHandleConnectionEventItem] | Unset = UNSET,

) -> SSEEvent | None:
    """ Subscribe to events from the Client.

    Args:
        event (list[EventControllerHandleConnectionEventItem] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SSEEvent
     """


    return sync_detailed(
        client=client,
event=event,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    event: list[EventControllerHandleConnectionEventItem] | Unset = UNSET,

) -> Response[SSEEvent]:
    """ Subscribe to events from the Client.

    Args:
        event (list[EventControllerHandleConnectionEventItem] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SSEEvent]
     """


    kwargs = _get_kwargs(
        event=event,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    event: list[EventControllerHandleConnectionEventItem] | Unset = UNSET,

) -> SSEEvent | None:
    """ Subscribe to events from the Client.

    Args:
        event (list[EventControllerHandleConnectionEventItem] | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SSEEvent
     """


    return (await asyncio_detailed(
        client=client,
event=event,

    )).parsed
