import asyncio
from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.clients.dummyjson import DummyJSONClient
from tickethub.mappers import build_users_by_id, map_todo_to_ticket_data
from tickethub.repositories.tickets import upsert_ticket


class TicketSourceClient(Protocol):
    async def get_todos(self) -> list[dict[str, Any]]: ...

    async def get_users(self) -> list[dict[str, Any]]: ...


async def sync_tickets(
    session: AsyncSession,
    client: TicketSourceClient | None = None,
) -> int:
    # Dohvaća podatke iz DummyJSON-a i sprema ih u lokalnu bazu
    source_client = client or DummyJSONClient()

    todos, users = await asyncio.gather(
        source_client.get_todos(),
        source_client.get_users(),
    )

    users_by_id = build_users_by_id(users)

    for todo in todos:
        ticket_data = map_todo_to_ticket_data(todo, users_by_id)
        await upsert_ticket(session, ticket_data)

    await session.commit()

    return len(todos)
