import asyncio
import logging
from typing import Any, Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.clients.dummyjson import DummyJSONClient
from tickethub.mappers import build_users_by_id, map_todo_to_ticket_data
from tickethub.repositories.tickets import upsert_ticket

logger = logging.getLogger(__name__)


class TicketSourceClient(Protocol):
    async def get_todos(self) -> list[dict[str, Any]]: ...

    async def get_users(self) -> list[dict[str, Any]]: ...


async def sync_tickets(
    session: AsyncSession,
    client: TicketSourceClient | None = None,
    overwrite_existing: bool = False,
) -> int:
    # Dohvaća podatke iz DummyJSON-a i sprema ih u lokalnu bazu
    logger.info("Pokretanje sinkronizacije ticketa.")

    source_client = client or DummyJSONClient()
    owns_client = client is None

    try:
        todos, users = await asyncio.gather(
            source_client.get_todos(),
            source_client.get_users(),
        )

        users_by_id = build_users_by_id(users)

        for todo in todos:
            ticket_data = map_todo_to_ticket_data(todo, users_by_id)
            await upsert_ticket(
                session=session,
                ticket_data=ticket_data,
                overwrite_existing=overwrite_existing,
            )

        await session.commit()

    finally:
        if owns_client and hasattr(source_client, "aclose"):
            await source_client.aclose()

    logger.info("Sinkronizacija završena. Broj ticketa: %s", len(todos))

    return len(todos)
