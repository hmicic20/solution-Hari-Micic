import logging
from typing import Any

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

    async def get_todos(self) -> list[dict[str, Any]]:
        # Dohvaća tickete iz DummyJSON todo endpointa
        logger.info("Dohvat ticketa iz DummyJSON servisa.")

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        ) as client:
            response = await client.get("/todos")
            response.raise_for_status()
            data = response.json()

        return data["todos"]

    async def get_users(self) -> list[dict[str, Any]]:
        # Dohvaća korisnike iz DummyJSON users endpointa
        logger.info("Dohvat korisnika iz DummyJSON servisa.")

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        ) as client:
            response = await client.get("/users")
            response.raise_for_status()
            data = response.json()

        return data["users"]
