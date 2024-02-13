from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar, overload

_P = ParamSpec("_P")
_R = TypeVar("_R")

class Client: ...

class AsyncClient(Client):
    async def emit(
        self,
        event: str,
        data: Any = None,
        namespace: str | None = None,
        callback: Callable[..., Any] | None = None,
    ) -> None: ...
    async def connect(
        self,
        url: str | Callable[[], str | Coroutine[Any, Any, str]],
        headers: dict[str, str] = ...,
        auth: dict[str, Any] | None = None,
        transports: str | list[str] | None = None,
        namespaces: str | list[str] | None = None,
        socketio_path: str = ...,
        wait: bool = True,
        wait_timeout: int = 1,
    ) -> None: ...
    async def disconnect(self) -> None: ...
    @overload
    def on(self, event: str, handler: Callable[_P, _R], namespace: str | None = None) -> None: ...
    @overload
    def on(
        self, event: str, namespace: str | None = None
    ) -> Callable[[Callable[_P, _R]], Callable[_P, _R]]: ...
