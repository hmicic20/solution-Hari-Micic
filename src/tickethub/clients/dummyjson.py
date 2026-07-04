import logging
from types import TracebackType
from typing import Any, Self

import httpx

logger = logging.getLogger(__name__)


class DummyJSONClient:
    def __init__(
        self,
        base_url: str = "https://dummyjson.com",
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        # Zatvara HTTP konekcije klijenta
        await self._client.aclose()

    async def get_todos(self) -> list[dict[str, Any]]:
        # Dohvaća tickete iz DummyJSON todo endpointa
        logger.info("Dohvat ticketa iz DummyJSON servisa.")

        response = await self._client.get("/todos", params={"limit": 0})
        response.raise_for_status()
        data = response.json()

        return data["todos"]

    async def get_users(self) -> list[dict[str, Any]]:
        # Dohvaća samo potrebna korisnička polja iz DummyJSON servisa
        logger.info("Dohvat korisnika iz DummyJSON servisa.")

        response = await self._client.get(
            "/users",
            params={"limit": 0, "select": "id,username"},
        )
        response.raise_for_status()
        data = response.json()

        return data["users"]
