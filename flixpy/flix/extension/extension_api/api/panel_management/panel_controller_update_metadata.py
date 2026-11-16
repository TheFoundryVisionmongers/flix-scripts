from http import HTTPStatus
from typing import Any, Dict, Optional, Union, cast

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.panel_update_metadata_request import PanelUpdateMetadataRequest
from ...models.panel_update_metadata_response import PanelUpdateMetadataResponse
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    json_body: PanelUpdateMetadataRequest,
    selected: Union[Unset, None, Any] = UNSET,
    range_: Union[Unset, None, Any] = UNSET,
    panel_ids: Union[Unset, None, Any] = UNSET,
) -> Dict[str, Any]:
    pass

    params: Dict[str, Any] = {}
    params["selected"] = selected

    params["range"] = range_

    params["panel_ids"] = panel_ids

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    json_json_body = json_body.to_dict()

    return {
        "method": "patch",
        "url": "/panels/metadata",
        "json": json_json_body,
        "params": params,
    }


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, PanelUpdateMetadataResponse]]:
    if response.status_code == HTTPStatus.OK:
        response_200 = PanelUpdateMetadataResponse.from_dict(response.json())

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
) -> Response[Union[Any, PanelUpdateMetadataResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    json_body: PanelUpdateMetadataRequest,
    selected: Union[Unset, None, Any] = UNSET,
    range_: Union[Unset, None, Any] = UNSET,
    panel_ids: Union[Unset, None, Any] = UNSET,
) -> Response[Union[Any, PanelUpdateMetadataResponse]]:
    """Update the metadata on the Panel Revisions from the currently loaded Sequence Revision.

     Updates panels metadata from the sequence revision currently open in the Panel Browser.

    Takes object with `metadata` key, which must be an `object` with key-value pairs, where the value is
    a `string` or `null`.

    If the value of the provided metadata key is `null`, the existing metadata for this key will be
    deleted.

    Query params can be used on their own or combined:

    - no params: all panels in the sequence revision

    - `selected=true`: only the currently selected panels

    - `range=2,5`: only the panels placed between 2nd and 5th panels (including 2nd and 5th)

    - `panel_ids=1,2,3`: only the panels with the given ids

    - `selected=true&panel_ids=1,2,3`: only the selected panels whose ids are in the list

    - `selected=true&range=2,5&panel_ids=1,2,3`: only the selected panels, positioned between 2nd and
    5th panels whose ids are in the list

    Returns list of update results, each including panel id and updated metadata.

    Args:
        selected (Union[Unset, None, Any]):  Example: selected=true.
        range_ (Union[Unset, None, Any]):  Example: range=1,5.
        panel_ids (Union[Unset, None, Any]):  Example: panel_ids=1,2,3.
        json_body (PanelUpdateMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PanelUpdateMetadataResponse]]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
        selected=selected,
        range_=range_,
        panel_ids=panel_ids,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    json_body: PanelUpdateMetadataRequest,
    selected: Union[Unset, None, Any] = UNSET,
    range_: Union[Unset, None, Any] = UNSET,
    panel_ids: Union[Unset, None, Any] = UNSET,
) -> Optional[Union[Any, PanelUpdateMetadataResponse]]:
    """Update the metadata on the Panel Revisions from the currently loaded Sequence Revision.

     Updates panels metadata from the sequence revision currently open in the Panel Browser.

    Takes object with `metadata` key, which must be an `object` with key-value pairs, where the value is
    a `string` or `null`.

    If the value of the provided metadata key is `null`, the existing metadata for this key will be
    deleted.

    Query params can be used on their own or combined:

    - no params: all panels in the sequence revision

    - `selected=true`: only the currently selected panels

    - `range=2,5`: only the panels placed between 2nd and 5th panels (including 2nd and 5th)

    - `panel_ids=1,2,3`: only the panels with the given ids

    - `selected=true&panel_ids=1,2,3`: only the selected panels whose ids are in the list

    - `selected=true&range=2,5&panel_ids=1,2,3`: only the selected panels, positioned between 2nd and
    5th panels whose ids are in the list

    Returns list of update results, each including panel id and updated metadata.

    Args:
        selected (Union[Unset, None, Any]):  Example: selected=true.
        range_ (Union[Unset, None, Any]):  Example: range=1,5.
        panel_ids (Union[Unset, None, Any]):  Example: panel_ids=1,2,3.
        json_body (PanelUpdateMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PanelUpdateMetadataResponse]
    """

    return sync_detailed(
        client=client,
        json_body=json_body,
        selected=selected,
        range_=range_,
        panel_ids=panel_ids,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    json_body: PanelUpdateMetadataRequest,
    selected: Union[Unset, None, Any] = UNSET,
    range_: Union[Unset, None, Any] = UNSET,
    panel_ids: Union[Unset, None, Any] = UNSET,
) -> Response[Union[Any, PanelUpdateMetadataResponse]]:
    """Update the metadata on the Panel Revisions from the currently loaded Sequence Revision.

     Updates panels metadata from the sequence revision currently open in the Panel Browser.

    Takes object with `metadata` key, which must be an `object` with key-value pairs, where the value is
    a `string` or `null`.

    If the value of the provided metadata key is `null`, the existing metadata for this key will be
    deleted.

    Query params can be used on their own or combined:

    - no params: all panels in the sequence revision

    - `selected=true`: only the currently selected panels

    - `range=2,5`: only the panels placed between 2nd and 5th panels (including 2nd and 5th)

    - `panel_ids=1,2,3`: only the panels with the given ids

    - `selected=true&panel_ids=1,2,3`: only the selected panels whose ids are in the list

    - `selected=true&range=2,5&panel_ids=1,2,3`: only the selected panels, positioned between 2nd and
    5th panels whose ids are in the list

    Returns list of update results, each including panel id and updated metadata.

    Args:
        selected (Union[Unset, None, Any]):  Example: selected=true.
        range_ (Union[Unset, None, Any]):  Example: range=1,5.
        panel_ids (Union[Unset, None, Any]):  Example: panel_ids=1,2,3.
        json_body (PanelUpdateMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, PanelUpdateMetadataResponse]]
    """

    kwargs = _get_kwargs(
        json_body=json_body,
        selected=selected,
        range_=range_,
        panel_ids=panel_ids,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    json_body: PanelUpdateMetadataRequest,
    selected: Union[Unset, None, Any] = UNSET,
    range_: Union[Unset, None, Any] = UNSET,
    panel_ids: Union[Unset, None, Any] = UNSET,
) -> Optional[Union[Any, PanelUpdateMetadataResponse]]:
    """Update the metadata on the Panel Revisions from the currently loaded Sequence Revision.

     Updates panels metadata from the sequence revision currently open in the Panel Browser.

    Takes object with `metadata` key, which must be an `object` with key-value pairs, where the value is
    a `string` or `null`.

    If the value of the provided metadata key is `null`, the existing metadata for this key will be
    deleted.

    Query params can be used on their own or combined:

    - no params: all panels in the sequence revision

    - `selected=true`: only the currently selected panels

    - `range=2,5`: only the panels placed between 2nd and 5th panels (including 2nd and 5th)

    - `panel_ids=1,2,3`: only the panels with the given ids

    - `selected=true&panel_ids=1,2,3`: only the selected panels whose ids are in the list

    - `selected=true&range=2,5&panel_ids=1,2,3`: only the selected panels, positioned between 2nd and
    5th panels whose ids are in the list

    Returns list of update results, each including panel id and updated metadata.

    Args:
        selected (Union[Unset, None, Any]):  Example: selected=true.
        range_ (Union[Unset, None, Any]):  Example: range=1,5.
        panel_ids (Union[Unset, None, Any]):  Example: panel_ids=1,2,3.
        json_body (PanelUpdateMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, PanelUpdateMetadataResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            json_body=json_body,
            selected=selected,
            range_=range_,
            panel_ids=panel_ids,
        )
    ).parsed
