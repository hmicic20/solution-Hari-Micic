import logging
from typing import Any

import httpx

from tickethub.schemas import AuthLoginRequest

logger = logging.getLogger(__name__)


class DummyJSONAuthClient:
    def __init__(
        self,
        base_url: str = "https://dummyjson.com",
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url
        self.timeout = timeout

    async def login(self, login_data: AuthLoginRequest) -> dict[str, Any]:
        # Šalje korisničke podatke DummyJSON auth servisu
        logger.info("Pokušaj prijave korisnika preko DummyJSON-a.")

        payload = {
            "username": login_data.username,
            "password": login_data.password,
            "expiresInMins": login_data.expires_in_mins,
        }

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        ) as client:
            response = await client.post("/auth/login", json=payload)
            response.raise_for_status()

            return response.json()

    async def get_current_user(self, access_token: str) -> dict[str, Any]:
        # Dohvaća trenutno prijavljenog korisnika preko JWT tokena
        logger.info("Dohvat trenutno prijavljenog korisnika.")

        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        ) as client:
            response = await client.get("/auth/me", headers=headers)
            response.raise_for_status()

            return response.json()
