"""Test mocking."""
from fastapi import FastAPI
import httpx
import pytest

from asgiar import ASGIAR

APP = FastAPI()


@APP.get("/foo", response_model=str)
async def foo() -> str:
    """Handle /foo."""
    return "bar"


HOST = "example.org"


@pytest.mark.asyncio
@ASGIAR(APP, host=HOST)
async def test_decorator():
    """Test using decorator.

    Calls to mocked hosts should be intercepted.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://{HOST}/foo")
        assert response.json() == "bar"


@pytest.mark.asyncio
async def test_context():
    """Test context manager.

    Calls to mocked hosts should be intercepted.
    """
    with ASGIAR(APP, host=HOST):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{HOST}/foo")
            assert response.status_code == 200
            assert response.json() == "bar"


@pytest.mark.asyncio
async def test_multiple():
    """Test multiple overlays.

    Calls to mocked hosts should be intercepted.
    """
    app1 = FastAPI()
    app2 = FastAPI()

    @app1.get("/foo", response_model=str)
    async def foo1() -> str:
        """Handle /foo."""
        return "app1"

    @app2.get("/foo", response_model=str)
    async def foo2() -> str:
        """Handle /foo."""
        return "app2"

    with ASGIAR(app1, host="abc.def"):
        with ASGIAR(app2, host="ghi.jkl"):
            async with httpx.AsyncClient() as client:
                response = await client.get("http://abc.def/foo")
                assert response.status_code == 200
                assert response.json() == "app1"

                response = await client.get("http://ghi.jkl/foo")
                assert response.status_code == 200
                assert response.json() == "app2"


@pytest.mark.asyncio
async def test_passthrough():
    """Test passthrough.

    Calls to hosts that are not mocked should behave normally.
    """
    with ASGIAR(APP, host="test"):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{HOST}")
            assert response.status_code == 200


def test_sync():
    """Test sync calling.

    The async overlay does nothing to sync calls.
    """
    with ASGIAR(APP, host=HOST):
        response = httpx.get(f"http://{HOST}")
        assert response.status_code == 200
        response = httpx.get(f"http://{HOST}/hello")
        assert response.status_code == 404
