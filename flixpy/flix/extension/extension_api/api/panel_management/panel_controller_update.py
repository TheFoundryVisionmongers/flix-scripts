from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.bulk_panel_request import BulkPanelRequest
from ...models.full_panel_request import FullPanelRequest
from ...models.panel_request_response import PanelRequestResponse
from typing import cast



def _get_kwargs(
    *,
    body: BulkPanelRequest | FullPanelRequest,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/panels",
    }

    
    if isinstance(body, BulkPanelRequest):
        _kwargs["json"] = body.to_dict()
    else:
        _kwargs["json"] = body.to_dict()


    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Any | PanelRequestResponse | None:
    if response.status_code == 200:
        response_200 = PanelRequestResponse.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Response[Any | PanelRequestResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: BulkPanelRequest | FullPanelRequest,

) -> Response[Any | PanelRequestResponse]:
    """ Update Existing Panels

     Updates existing panels in the active sequence revision from the list of provided file paths.

    Args:
        body (BulkPanelRequest | FullPanelRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | PanelRequestResponse]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)

def sync(
    *,
    client: AuthenticatedClient,
    body: BulkPanelRequest | FullPanelRequest,

) -> Any | PanelRequestResponse | None:
    """ Update Existing Panels

     Updates existing panels in the active sequence revision from the list of provided file paths.

    Args:
        body (BulkPanelRequest | FullPanelRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | PanelRequestResponse
     """


    return sync_detailed(
        client=client,
body=body,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: BulkPanelRequest | FullPanelRequest,

) -> Response[Any | PanelRequestResponse]:
    """ Update Existing Panels

     Updates existing panels in the active sequence revision from the list of provided file paths.

    Args:
        body (BulkPanelRequest | FullPanelRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | PanelRequestResponse]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    body: BulkPanelRequest | FullPanelRequest,

) -> Any | PanelRequestResponse | None:
    """ Update Existing Panels

     Updates existing panels in the active sequence revision from the list of provided file paths.

    Args:
        body (BulkPanelRequest | FullPanelRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | PanelRequestResponse
     """


    return (await asyncio_detailed(
        client=client,
body=body,

    )).parsed
