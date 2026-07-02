from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.database import get_db_session
from tickethub.models import Ticket
from tickethub.repositories.tickets import (
    create_ticket,
    get_ticket_by_id,
    list_tickets,
    search_tickets,
    update_ticket,
)
from tickethub.schemas import (
    TicketCreate,
    TicketDetail,
    TicketListItem,
    TicketListResponse,
    TicketPriority,
    TicketStatus,
    TicketUpdate,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])


def to_ticket_list_item(ticket: Ticket) -> TicketListItem:
    # Skraćuje opis za prikaz u listi
    description = ticket.description

    if description is not None and len(description) > 100:
        description = description[:100]

    return TicketListItem(
        id=ticket.id,
        title=ticket.title,
        status=ticket.status,
        priority=ticket.priority,
        description=description,
    )


@router.get("", response_model=TicketListResponse)
async def get_tickets(
    status_filter: TicketStatus | None = Query(default=None, alias="status"),
    priority_filter: TicketPriority | None = Query(default=None, alias="priority"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> TicketListResponse:
    # Vraća paginiranu listu ticketa iz lokalne baze
    tickets, total = await list_tickets(
        session=session,
        status=status_filter.value if status_filter else None,
        priority=priority_filter.value if priority_filter else None,
        limit=limit,
        offset=offset,
    )

    return TicketListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[to_ticket_list_item(ticket) for ticket in tickets],
    )


@router.get("/search", response_model=TicketListResponse)
async def search_tickets_endpoint(
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> TicketListResponse:
    # Pretražuje tickete po nazivu
    tickets, total = await search_tickets(
        session=session,
        q=q,
        limit=limit,
        offset=offset,
    )

    return TicketListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[to_ticket_list_item(ticket) for ticket in tickets],
    )


@router.get("/{ticket_id}", response_model=TicketDetail)
async def get_ticket_detail(
    ticket_id: int,
    session: AsyncSession = Depends(get_db_session),
) -> TicketDetail:
    # Vraća detalje jednog ticketa
    ticket = await get_ticket_by_id(session=session, ticket_id=ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket nije pronađen.",
        )

    return TicketDetail.model_validate(ticket)


@router.post("", response_model=TicketDetail, status_code=status.HTTP_201_CREATED)
async def create_ticket_endpoint(
    ticket_data: TicketCreate,
    session: AsyncSession = Depends(get_db_session),
) -> TicketDetail:
    # Kreira novi ticket
    ticket = await create_ticket(
        session=session,
        ticket_data=ticket_data,
    )

    return TicketDetail.model_validate(ticket)


@router.patch("/{ticket_id}", response_model=TicketDetail)
async def update_ticket_endpoint(
    ticket_id: int,
    ticket_data: TicketUpdate,
    session: AsyncSession = Depends(get_db_session),
) -> TicketDetail:
    # Mijenja postojeći ticket
    ticket = await get_ticket_by_id(session=session, ticket_id=ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket nije pronađen.",
        )

    updated_ticket = await update_ticket(
        session=session,
        ticket=ticket,
        ticket_data=ticket_data,
    )

    return TicketDetail.model_validate(updated_ticket)
