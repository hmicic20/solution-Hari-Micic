from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.models import Ticket
from tickethub.schemas import TicketCreate, TicketUpdate


async def get_ticket_by_external_id(
    session: AsyncSession,
    source_system: str,
    external_id: int,
) -> Ticket | None:
    # Traži seed ticket prema izvoru i vanjskom ID-u
    result = await session.execute(
        select(Ticket).where(
            Ticket.source_system == source_system,
            Ticket.external_id == external_id,
        )
    )
    return result.scalar_one_or_none()


async def upsert_ticket(
    session: AsyncSession,
    ticket_data: dict[str, Any],
    overwrite_existing: bool = False,
) -> Ticket:
    # Sprema seed ticket bez miješanja lokalnog ID-a i vanjskog ID-a
    source_system = ticket_data.get("source_system")
    external_id = ticket_data.get("external_id")

    existing_ticket: Ticket | None = None

    if source_system is not None and external_id is not None:
        existing_ticket = await get_ticket_by_external_id(
            session=session,
            source_system=source_system,
            external_id=external_id,
        )

    if existing_ticket is None:
        ticket = Ticket(**ticket_data)
        session.add(ticket)
        return ticket

    if overwrite_existing:
        for field_name, field_value in ticket_data.items():
            setattr(existing_ticket, field_name, field_value)

    return existing_ticket


async def get_ticket_by_id(
    session: AsyncSession,
    ticket_id: int,
) -> Ticket | None:
    # Dohvaća jedan ticket prema ID-u
    return await session.get(Ticket, ticket_id)


async def list_tickets(
    session: AsyncSession,
    status: str | None = None,
    priority: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Ticket], int]:
    # Dohvaća paginiranu listu ticketa uz opcionalne filtere
    conditions = []

    if status is not None:
        conditions.append(Ticket.status == status)

    if priority is not None:
        conditions.append(Ticket.priority == priority)

    query = select(Ticket).order_by(Ticket.id).limit(limit).offset(offset)
    count_query = select(func.count()).select_from(Ticket)

    if conditions:
        query = query.where(*conditions)
        count_query = count_query.where(*conditions)

    tickets_result = await session.execute(query)
    total_result = await session.execute(count_query)

    tickets = list(tickets_result.scalars().all())
    total = total_result.scalar_one()

    return tickets, total


async def search_tickets(
    session: AsyncSession,
    q: str,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Ticket], int]:
    # Pretražuje tickete po nazivu
    search_pattern = f"%{q}%"

    query = (
        select(Ticket)
        .where(Ticket.title.ilike(search_pattern))
        .order_by(Ticket.id)
        .limit(limit)
        .offset(offset)
    )

    count_query = (
        select(func.count())
        .select_from(Ticket)
        .where(Ticket.title.ilike(search_pattern))
    )

    tickets_result = await session.execute(query)
    total_result = await session.execute(count_query)

    tickets = list(tickets_result.scalars().all())
    total = total_result.scalar_one()

    return tickets, total


async def create_ticket(
    session: AsyncSession,
    ticket_data: TicketCreate,
) -> Ticket:
    # Kreira novi ticket objekt, ali ne radi commit
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        status=ticket_data.status.value,
        priority=ticket_data.priority.value,
        assignee=ticket_data.assignee,
        source_payload=None,
    )

    session.add(ticket)

    return ticket


async def update_ticket(
    session: AsyncSession,
    ticket: Ticket,
    ticket_data: TicketUpdate,
) -> Ticket:
    # Mijenja postojeći ticket objekt, ali ne radi commit
    update_data = ticket_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value

        setattr(ticket, field, value)

    return ticket
