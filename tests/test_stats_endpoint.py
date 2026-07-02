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


@pytest.mark.asyncio
async def test_get_stats_returns_ticket_statistics(
    client: AsyncClient,
    session_maker: async_sessionmaker,
) -> None:
    async with session_maker() as session:
        session.add_all(
            [
                Ticket(
                    id=1,
                    title="Ticket 1",
                    description="Opis 1",
                    status="open",
                    priority="low",
                    assignee="ana",
                    source_payload={"id": 1},
                ),
                Ticket(
                    id=2,
                    title="Ticket 2",
                    description="Opis 2",
                    status="closed",
                    priority="high",
                    assignee="ivan",
                    source_payload={"id": 2},
                ),
                Ticket(
                    id=3,
                    title="Ticket 3",
                    description="Opis 3",
                    status="open",
                    priority="high",
                    assignee="marko",
                    source_payload={"id": 3},
                ),
            ]
        )

        await session.commit()

    response = await client.get("/stats")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["by_status"] == {
        "closed": 1,
        "open": 2,
    }
    assert data["by_priority"] == {
        "high": 2,
        "low": 1,
    }
