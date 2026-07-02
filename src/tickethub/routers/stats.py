from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.database import get_db_session
from tickethub.repositories.stats import get_ticket_stats
from tickethub.schemas import TicketStatsResponse


router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=TicketStatsResponse)
async def get_stats(
    session: AsyncSession = Depends(get_db_session),
) -> TicketStatsResponse:
    # Vraća osnovne statistike ticketa
    stats = await get_ticket_stats(session)

    return TicketStatsResponse(**stats)