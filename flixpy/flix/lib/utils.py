import time
from typing import ParamSpec, Callable, TypeVar, Awaitable

Params = ParamSpec("Params")
ReturnType = TypeVar("ReturnType")
AsyncFunction = Callable[Params, Awaitable[ReturnType]]


def cache(
    seconds: float,
) -> Callable[[AsyncFunction[Params, ReturnType]], AsyncFunction[Params, ReturnType]]:
    def decorator(f: AsyncFunction[Params, ReturnType]) -> AsyncFunction[Params, ReturnType]:
        cached_value: ReturnType | None = None
        last_called = time.time()

        async def wrapper(*args: Params.args, **kwargs: Params.kwargs) -> ReturnType:
            nonlocal cached_value, last_called
            if cached_value is not None and time.time() - last_called < seconds:
                return cached_value

            cached_value = await f(*args, **kwargs)
            last_called = time.time()
            return cached_value

        return wrapper

    return decorator
