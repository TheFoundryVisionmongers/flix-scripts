from http import HTTPStatus
from typing import Any, cast
from urllib.parse import quote

import httpx2

from ...client import AuthenticatedClient, Client
from ...types import Response, UNSET
from ... import errors

from ...models.project_details_metadata_dto import ProjectDetailsMetadataDto
from typing import cast



def _get_kwargs(
    *,
    body: ProjectDetailsMetadataDto,

) -> dict[str, Any]:
    headers: dict[str, Any] = {}


    

    

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/project/metadata",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs



def _parse_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Any | None:
    if response.status_code == 200:
        return None

    if response.status_code == 400:
        return None

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(*, client: AuthenticatedClient | Client, response: httpx2.Response) -> Response[Any]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    body: ProjectDetailsMetadataDto,

) -> Response[Any]:
    """ Update Entity Metadata in Current Project

     Merges custom metadata into the target entity (show, episode, sequence, or sequence-revision) within
    the active project context.Requested entities must exist in the current project context.
    ### Convention & Best Practices:
    - Prefix keys with your extension/plugin identifier (e.g. `com.vendor.plugin:key`) to avoid
    collisions.
    - Only keys provided are updated; omitted keys remain untouched.
    - If the key does not exist, it will be created unless its value is `null`.
    - Set a key's value to `null` to delete it.
    - If the key does not exist with the specified name and `null` is provided as its value, it will be
    ignored.

    Args:
        body (ProjectDetailsMetadataDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    body: ProjectDetailsMetadataDto,

) -> Response[Any]:
    """ Update Entity Metadata in Current Project

     Merges custom metadata into the target entity (show, episode, sequence, or sequence-revision) within
    the active project context.Requested entities must exist in the current project context.
    ### Convention & Best Practices:
    - Prefix keys with your extension/plugin identifier (e.g. `com.vendor.plugin:key`) to avoid
    collisions.
    - Only keys provided are updated; omitted keys remain untouched.
    - If the key does not exist, it will be created unless its value is `null`.
    - Set a key's value to `null` to delete it.
    - If the key does not exist with the specified name and `null` is provided as its value, it will be
    ignored.

    Args:
        body (ProjectDetailsMetadataDto):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx2.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Any]
     """


    kwargs = _get_kwargs(
        body=body,

    )

    response = await client.get_async_httpx_client().request(
        **kwargs
    )

    return _build_response(client=client, response=response)

