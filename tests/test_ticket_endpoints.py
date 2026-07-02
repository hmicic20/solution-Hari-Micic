from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tickethub.database import Base, get_db_session
from tickethub.main import app
from tickethub.models import Ticket


@pytest_asyncio.fixture
async def session_maker() -> AsyncGenerator[async_sessionmaker, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    test_session_maker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    yield test_session_maker

    await engine.dispose()


@pytest_asyncio.fixture
async def client(
    session_maker: async_sessionmaker,
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db_session() -> AsyncGenerator:
        async with session_maker() as session:
            yield session

    app.dependency_overrides[get_db_session] = override_get_db_session

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


async def seed_tickets(session_maker: async_sessionmaker) -> None:
    async with session_maker() as session:
        session.add_all(
            [
                Ticket(
                    id=1,
                    title="Fix printer issue",
                    description="A" * 150,
                    status="open",
                    priority="low",
                    assignee="ana",
                    source_payload={"id": 1},
                ),
                Ticket(
                    id=2,
                    title="Close old account",
                    description="Old account needs to be closed.",
                    status="closed",
                    priority="high",
                    assignee="ivan",
                    source_payload={"id": 2},
                ),
            ]
        )

        await session.commit()


@pytest.mark.asyncio
async def test_get_tickets_returns_paginated_list(
    client: AsyncClient,
    session_maker: async_sessionmaker,
) -> None:
    await seed_tickets(session_maker)

    response = await client.get("/tickets")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert data["limit"] == 20
    assert data["offset"] == 0
    assert len(data["items"]) == 2
    assert len(data["items"][0]["description"]) == 100


@pytest.mark.asyncio
async def test_get_tickets_can_filter_by_status_and_priority(
    client: AsyncClient,
    session_maker: async_sessionmaker,
) -> None:
    await seed_tickets(session_maker)

    response = await client.get("/tickets?status=closed&priority=high")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["title"] == "Close old account"


@pytest.mark.asyncio
async def test_search_tickets_by_title(
    client: AsyncClient,
    session_maker: async_sessionmaker,
) -> None:
    await seed_tickets(session_maker)

    response = await client.get("/tickets/search?q=printer")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 1
    assert data["items"][0]["title"] == "Fix printer issue"


@pytest.mark.asyncio
async def test_get_ticket_detail(
    client: AsyncClient,
    session_maker: async_sessionmaker,
) -> None:
    await seed_tickets(session_maker)

    response = await client.get("/tickets/1")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["title"] == "Fix printer issue"
    assert data["source_payload"] == {"id": 1}


@pytest.mark.asyncio
async def test_get_ticket_detail_returns_404_for_missing_ticket(
    client: AsyncClient,
) -> None:
    response = await client.get("/tickets/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Ticket nije pronađen."