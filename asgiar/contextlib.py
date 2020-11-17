"""AsyncContextDecorator."""
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable


class AsyncContextDecorator(ABC):
    """AsyncContextDecorator."""

    def __call__(self, func: Callable):
        """Decorate."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with self:
                await func(*args, **kwargs)
        return wrapper

    @abstractmethod
    async def __aenter__(self) -> "AsyncContextDecorator":
        """Enter async context."""

    @abstractmethod
    async def __aexit__(self, *args: Any) -> None:
        """Exit async context."""


class AsyncContextManager(AsyncContextDecorator):
    """AsyncContextManager."""

    def __init__(self, generator):
        """Initialize."""
        self._generator = generator

    async def __aenter__(self):
        """Enter async context."""
        return await self._generator.__anext__()

    async def __aexit__(self, *args):
        """Exit async context."""
        try:
            await self._generator.__anext__()
        except StopIteration:
            return


def asynccontextmanager(func):
    """Decorate function, turning it into a context manager and decorator."""
    @wraps(func)
    def helper(*args, **kwargs):
        return AsyncContextManager(func(*args, **kwargs))
    return helper
