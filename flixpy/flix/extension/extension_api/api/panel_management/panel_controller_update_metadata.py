from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.panel_update_metadata_request import PanelUpdateMetadataRequest
from ...models.panel_update_metadata_response import PanelUpdateMetadataResponse
from ...types import UNSET, Unset
from typing import cast



def _get_kwargs(
    *,
    body: PanelUpdateMetadataRequest,
    selected: Any | Unset = UNSET,
    range_: Any | Unset = UNSET,
    panel_ids: Any | Unset = UNSET,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    params: dict[str, Any] = {}

    params["selected"] = selected

    params["range"] = range_

    params["panel_ids"] = panel_ids


    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}


    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/panels/metadata",
        "params": params,
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Any | PanelUpdateMetadataResponse | None:
    if response.status_code == 200:
        response_200 = PanelUpdateMetadataResponse.from_dict(response.json())



        return response_200

    if response.status_code == 400:
        response_400 = cast(Any, None)
        return response_400

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Response[Any | PanelUpdateMetadataResponse]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: PanelUpdateMetadataRequest,
    selected: Any | Unset = UNSET,
    range_: Any | Unset = UNSET,
    panel_ids: Any | Unset = UNSET,

) -> Response[Any | PanelUpdateMetadataResponse]:
    """ Update the metadata on the Panel Revisions from the currently loaded Sequence Revision.

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
        selected (Any | Unset):  Example: selected=true.
        range_ (Any | Unset):  Example: range=1,5.
        panel_ids (Any | Unset):  Example: panel_ids=1,2,3.
        body (PanelUpdateMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | PanelUpdateMetadataResponse]
     """


    kwargs = _get_kwargs(
        body=body,
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
    body: PanelUpdateMetadataRequest,
    selected: Any | Unset = UNSET,
    range_: Any | Unset = UNSET,
    panel_ids: Any | Unset = UNSET,

) -> Any | PanelUpdateMetadataResponse | None:
    """ Update the metadata on the Panel Revisions from the currently loaded Sequence Revision.

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
        selected (Any | Unset):  Example: selected=true.
        range_ (Any | Unset):  Example: range=1,5.
        panel_ids (Any | Unset):  Example: panel_ids=1,2,3.
        body (PanelUpdateMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | PanelUpdateMetadataResponse
     """


    return sync_detailed(
        client=client,
body=body,
selected=selected,
range_=range_,
panel_ids=panel_ids,

    ).parsed

async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: PanelUpdateMetadataRequest,
    selected: Any | Unset = UNSET,
    range_: Any | Unset = UNSET,
    panel_ids: Any | Unset = UNSET,

) -> Response[Any | PanelUpdateMetadataResponse]:
    """ Update the metadata on the Panel Revisions from the currently loaded Sequence Revision.

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
        selected (Any | Unset):  Example: selected=true.
        range_ (Any | Unset):  Example: range=1,5.
        panel_ids (Any | Unset):  Example: panel_ids=1,2,3.
        body (PanelUpdateMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any | PanelUpdateMetadataResponse]
     """


    kwargs = _get_kwargs(
        body=body,
selected=selected,
range_=range_,
panel_ids=panel_ids,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

async def asyncio(
    *,
    client: AuthenticatedClient,
    body: PanelUpdateMetadataRequest,
    selected: Any | Unset = UNSET,
    range_: Any | Unset = UNSET,
    panel_ids: Any | Unset = UNSET,

) -> Any | PanelUpdateMetadataResponse | None:
    """ Update the metadata on the Panel Revisions from the currently loaded Sequence Revision.

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
        selected (Any | Unset):  Example: selected=true.
        range_ (Any | Unset):  Example: range=1,5.
        panel_ids (Any | Unset):  Example: panel_ids=1,2,3.
        body (PanelUpdateMetadataRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Any | PanelUpdateMetadataResponse
     """


    return (await asyncio_detailed(
        client=client,
body=body,
selected=selected,
range_=range_,
panel_ids=panel_ids,

    )).parsed
