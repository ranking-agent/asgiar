"""ASGI AR."""
import asyncio
from fnmatch import fnmatch
from functools import partial, wraps
from typing import Any, List
from unittest import mock
from urllib.parse import urlparse

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
            url: str = None,
    ) -> None:
        """Initialize."""
        self._patches: List[mock._patch] = []
        self._transport = httpx.ASGITransport(app=asgi_app)
        if host is not None:
            self._host: str = host.lower()
        if url is not None:
            parsed = urlparse(url)
            self._url_prefix: str = f"{parsed.scheme}://{parsed.netloc}"
            self._url_path: str = parsed.path
        else:
            self._url_prefix = f"http://{self._host}"
            self._url_path = "/*"
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
            if "url" not in kwargs:
                return await pass_through(*args, **kwargs)
            scheme, host, port, path = kwargs["url"]
            prefix = scheme.decode() + "://" + host.decode() + (":" + port.decode() if port is not None else "")
            path = path.decode()
            if prefix == self._url_prefix and fnmatch(path, self._url_path):
                timeout = kwargs.get("extensions", {}).get("timeout", {"read": None})["read"]
                return await asyncio.wait_for(self._transport.handle_async_request(
                    *args,
                    **kwargs,
                ), timeout=timeout)
            return await pass_through(*args, **kwargs)

        return request
