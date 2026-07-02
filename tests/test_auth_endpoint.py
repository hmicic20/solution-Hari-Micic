import pytest
from httpx import ASGITransport, AsyncClient

from tickethub.main import app


@pytest.mark.asyncio
async def test_auth_me_requires_bearer_token() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Nedostaje Bearer token."


@pytest.mark.asyncio
async def test_auth_login_rejects_empty_payload() -> None:
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/login",
            json={
                "username": "",
                "password": "",
            },
        )

    assert response.status_code == 422
