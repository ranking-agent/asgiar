# ARCHIVED: This repo was developed for tests in the Strider repo, but is no longer being used.

# ASGIAR

**A**synchronous **S**erver **G**ateway **I**nterface - **A**ugmented **R**eality

ASGIAR mounts an [ASGI](https://asgi.readthedocs.io/en/latest/) application at a specified host and overlays it on top of the "real world", i.e. your typical network interfaces.

This augmented reality is available through [`httpcore`](https://github.com/encode/httpcore) and higher-level interfaces that use it, in particular [`httpx`](https://github.com/encode/httpx).

## Example

```python
import asyncio

from asgiar import ASGIAR
from fastapi import FastAPI
import httpx

APP = FastAPI()


async def test():
    """Handle /test."""
    return "OK"
APP.get("/test")(test)


async def main():
    """Run example."""
    with ASGIAR(APP, host="asgiar"):
        async with httpx.AsyncClient() as client:
            response = await client.get("http://asgiar/test")
        assert response.status_code == 200


if __name__ == "__main__":
    asyncio.run(main())
```

ASGIAR can be used as a context manager or a decorator.

ASGIAR behaves like you expect:

* you may use ASGIAR in nested fashion to mock multiple hosts
* if you make a request of an un-mocked host, you receive the genuine item
* if you mock an existing host, the original becomes unreachable

### Limitations

* ASGIAR mocks an entire host -  you may not pass through a subset of endpoints
* your augmented reality can only be reached through `httpcore` (`httpx`) while making asynchronous requests, e.g. using [`httpx.AsyncClient`](https://www.python-httpx.org/async/)

## ASGI applications

Popular frameworks for producing ASGI applications include:

* [FastAPI](https://github.com/tiangolo/fastapi)
* [Starlette](https://github.com/encode/starlette)
* [Sanic](https://github.com/huge-success/sanic)
