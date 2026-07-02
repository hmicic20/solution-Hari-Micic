from typing import Any

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tickethub.database import Base
from tickethub.models import Ticket
from tickethub.services.sync_service import sync_tickets


class FakeDummyJSONClient:
    async def get_todos(self) -> list[dict[str, Any]]:
        return [
            {
                "id": 1,
                "todo": "Fix printer issue",
                "completed": False,
                "userId": 2,
            },
            {
                "id": 2,
                "todo": "Close old account",
                "completed": True,
                "userId": 1,
            },
        ]

    async def get_users(self) -> list[dict[str, Any]]:
        return [
            {"id": 1, "username": "ivan"},
            {"id": 2, "username": "ana"},
        ]


@pytest.mark.asyncio
async def test_sync_tickets_saves_tickets_to_database() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async with session_maker() as session:
        synced_count = await sync_tickets(
            session=session,
            client=FakeDummyJSONClient(),
        )

        saved_ticket = await session.get(Ticket, 1)

    await engine.dispose()

    assert synced_count == 2
    assert saved_ticket is not None
    assert saved_ticket.title == "Fix printer issue"
    assert saved_ticket.status == "open"
    assert saved_ticket.priority == "low"
    assert saved_ticket.assignee == "ana"


@pytest.mark.asyncio
async def test_sync_tickets_does_not_overwrite_existing_ticket_by_default() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    async with session_maker() as session:
        session.add(
            Ticket(
                id=1,
                title="Local edited title",
                description="Local edited description",
                status="closed",
                priority="high",
                assignee="petra",
                source_payload={"id": 1},
            )
        )
        await session.commit()

        await sync_tickets(
            session=session,
            client=FakeDummyJSONClient(),
        )

        saved_ticket = await session.get(Ticket, 1)

    await engine.dispose()

    assert saved_ticket is not None
    assert saved_ticket.title == "Local edited title"
    assert saved_ticket.status == "closed"
    assert saved_ticket.priority == "high"
    assert saved_ticket.assignee == "petra"
