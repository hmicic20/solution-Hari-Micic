import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from tickethub.database import Base
from tickethub.models import Ticket
from tickethub.services.sync_service import sync_tickets


class FakeDummyJSONClient:
    async def get_todos(self) -> list[dict]:
        return [
            {
                "id": 1,
                "todo": "First source ticket",
                "completed": False,
                "userId": 1,
            },
            {
                "id": 2,
                "todo": "Second source ticket",
                "completed": False,
                "userId": 2,
            },
        ]

    async def get_users(self) -> list[dict]:
        return [
            {"id": 1, "username": "ana"},
            {"id": 2, "username": "petra"},
        ]


class UpdatedFakeDummyJSONClient:
    async def get_todos(self) -> list[dict]:
        return [
            {
                "id": 1,
                "todo": "Updated from source",
                "completed": True,
                "userId": 1,
            },
            {
                "id": 2,
                "todo": "Second source ticket",
                "completed": False,
                "userId": 2,
            },
        ]

    async def get_users(self) -> list[dict]:
        return [
            {"id": 1, "username": "ana"},
            {"id": 2, "username": "petra"},
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

        result = await session.execute(
            select(Ticket).where(
                Ticket.source_system == "dummyjson",
                Ticket.external_id == 1,
            )
        )
        saved_ticket = result.scalar_one_or_none()

    await engine.dispose()

    assert synced_count == 2
    assert saved_ticket is not None
    assert saved_ticket.title == "First source ticket"
    assert saved_ticket.status == "open"
    assert saved_ticket.priority == "low"
    assert saved_ticket.assignee == "ana"
    assert saved_ticket.source_system == "dummyjson"
    assert saved_ticket.external_id == 1
    assert saved_ticket.locally_modified is False


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


@pytest.mark.asyncio
async def test_sync_tickets_is_idempotent_for_seed_data() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_maker() as session:
        await sync_tickets(session=session, client=FakeDummyJSONClient())
        await sync_tickets(session=session, client=FakeDummyJSONClient())

        total = await session.scalar(select(func.count()).select_from(Ticket))

    await engine.dispose()

    assert total == 2


@pytest.mark.asyncio
async def test_sync_refreshes_unmodified_seed_ticket() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_maker() as session:
        await sync_tickets(session=session, client=FakeDummyJSONClient())
        await sync_tickets(session=session, client=UpdatedFakeDummyJSONClient())

        result = await session.execute(
            select(Ticket).where(
                Ticket.source_system == "dummyjson",
                Ticket.external_id == 1,
            )
        )
        ticket = result.scalar_one()

    await engine.dispose()

    assert ticket.title == "Updated from source"
    assert ticket.status == "closed"
    assert ticket.locally_modified is False


@pytest.mark.asyncio
async def test_sync_does_not_overwrite_locally_modified_seed_ticket() -> None:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    async with session_maker() as session:
        await sync_tickets(session=session, client=FakeDummyJSONClient())

        result = await session.execute(
            select(Ticket).where(
                Ticket.source_system == "dummyjson",
                Ticket.external_id == 1,
            )
        )
        ticket = result.scalar_one()
        ticket.title = "Local manual title"
        ticket.priority = "high"
        ticket.locally_modified = True

        await session.commit()

        await sync_tickets(session=session, client=UpdatedFakeDummyJSONClient())

        result = await session.execute(
            select(Ticket).where(
                Ticket.source_system == "dummyjson",
                Ticket.external_id == 1,
            )
        )
        updated_ticket = result.scalar_one()

    await engine.dispose()

    assert updated_ticket.title == "Local manual title"
    assert updated_ticket.priority == "high"
    assert updated_ticket.locally_modified is True
    assert updated_ticket.source_payload["todo"] == "Updated from source"
