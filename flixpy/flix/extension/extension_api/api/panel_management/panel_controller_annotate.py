from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.bulk_panel_annotate_request import BulkPanelAnnotateRequest
from ...models.full_panel_annotate_request import FullPanelAnnotateRequest
from ...models.panel_request_response import PanelRequestResponse
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


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, PanelRequestResponse]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PanelRequestResponse.from_dict(response.json())

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
) -> Response[Union[Any, PanelRequestResponse]]:
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
) -> Response[Union[Any, PanelRequestResponse]]:
    """Update Panel Annotations

     Adds annotations to panels in the active sequence revision from the list of provided file paths.

    Args:
        json_body (Union['BulkPanelAnnotateRequest', 'FullPanelAnnotateRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PanelRequestResponse]]
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
    json_body: Union["BulkPanelAnnotateRequest", "FullPanelAnnotateRequest"],
) -> Optional[Union[Any, PanelRequestResponse]]:
    """Update Panel Annotations

     Adds annotations to panels in the active sequence revision from the list of provided file paths.

    Args:
        json_body (Union['BulkPanelAnnotateRequest', 'FullPanelAnnotateRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PanelRequestResponse]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    json_body: Union["BulkPanelAnnotateRequest", "FullPanelAnnotateRequest"],
) -> Response[Union[Any, PanelRequestResponse]]:
    """Update Panel Annotations

     Adds annotations to panels in the active sequence revision from the list of provided file paths.

    Args:
        json_body (Union['BulkPanelAnnotateRequest', 'FullPanelAnnotateRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PanelRequestResponse]]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    json_body: Union["BulkPanelAnnotateRequest", "FullPanelAnnotateRequest"],
) -> Optional[Union[Any, PanelRequestResponse]]:
    """Update Panel Annotations

     Adds annotations to panels in the active sequence revision from the list of provided file paths.

    Args:
        json_body (Union['BulkPanelAnnotateRequest', 'FullPanelAnnotateRequest']):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PanelRequestResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
        )
    ).parsed
