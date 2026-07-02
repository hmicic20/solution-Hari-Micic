from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.models import Ticket


async def upsert_ticket(
    session: AsyncSession,
    ticket_data: dict[str, Any],
) -> Ticket:
    # Sprema novi ticket ili ažurira postojeći prema ID-u
    ticket = await session.get(Ticket, ticket_data["id"])

    if ticket is None:
        ticket = Ticket(**ticket_data)
        session.add(ticket)
        return ticket

    for field, value in ticket_data.items():
        setattr(ticket, field, value)

    return ticket