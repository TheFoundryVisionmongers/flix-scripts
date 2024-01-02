from http import HTTPStatus
from typing import Any, Dict, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bulk_panel_annotate_request import BulkPanelAnnotateRequest
from ...models.full_panel_annotate_request import FullPanelAnnotateRequest
from ...types import Response


def _get_kwargs(
    *,
    json_body: Union["BulkPanelAnnotateRequest", "FullPanelAnnotateRequest"],
) -> Dict[str, Any]:
    pass

    json_json_body: Dict[str, Any]

    if isinstance(json_body, BulkPanelAnnotateRequest):
        json_json_body = json_body.to_dict()

    else:
        json_json_body = json_body.to_dict()

    return {
        "method": "patch",
        "url": "/panels/annotate",
        "json": json_json_body,
    }


def _parse_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Optional[Any]:
    if response.status_code == HTTPStatus.OK:
        return None
    if response.status_code == HTTPStatus.BAD_REQUEST:
        return None
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: Union[AuthenticatedClient, Client], response: httpx.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    json_body: Union["BulkPanelAnnotateRequest", "FullPanelAnnotateRequest"],
) -> Response[Any]:
    """
    Args:
        json_body (Union['BulkPanelAnnotateRequest', 'FullPanelAnnotateRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    json_body: Union["BulkPanelAnnotateRequest", "FullPanelAnnotateRequest"],
) -> Response[Any]:
    """
    Args:
        json_body (Union['BulkPanelAnnotateRequest', 'FullPanelAnnotateRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)
