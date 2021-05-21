"""ASGI AR."""
from functools import partial, wraps
from typing import Any, List
from unittest import mock

import httpx

from .contextlib import AsyncContextDecorator


class ASGIAR(AsyncContextDecorator):
    """ASGI AR."""

    _targets = [
        "httpcore._async.connection.AsyncHTTPConnection",
        "httpcore._async.connection_pool.AsyncConnectionPool",
        "httpcore._async.http_proxy.AsyncHTTPProxy",
    ]

    def __init__(
            self,
            asgi_app,
            host: str = None,
    ) -> None:
        """Initialize."""
        self._patches: List[mock._patch] = []
        self._transport = httpx.ASGITransport(app=asgi_app)
        self._host: str = host.lower()
        super().__init__()

    def __enter__(self) -> "ASGIAR":
        """Start patching."""
        if self._patches:
            return self

        for transport in self._targets:
            patch = mock.patch(
                f"{transport}.handle_async_request",
                spec=True,
                new_callable=self._handle_async_request,
            )
            patch.start()
            self._patches.append(patch)

        return self

    def __exit__(self, *args: Any) -> None:
        """Stop patching."""
        while self._patches:
            patch = self._patches.pop()
            patch.stop()

    async def __aenter__(self) -> "ASGIAR":
        """Start patching."""
        return self.__enter__()

    async def __aexit__(self, *args: Any) -> None:
        """Stop patching."""
        self.__exit__(*args)

    def _handle_async_request(self, spec):
        async def request(_self, *args, **kwargs):
            pass_through = partial(spec, _self)
            host = args[1][1].decode()
            if self._host is None or host == self._host:
                return await self._transport.handle_async_request(
                    *args,
                    **kwargs,
                )
            return await pass_through(*args, **kwargs)

        return request
