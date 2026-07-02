from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.cache import get_cache, set_cache
from tickethub.database import get_db_session
from tickethub.repositories.stats import get_ticket_stats
from tickethub.schemas import TicketStatsResponse

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("", response_model=TicketStatsResponse)
async def get_stats(
    session: AsyncSession = Depends(get_db_session),
) -> TicketStatsResponse:
    # Vraća osnovne statistike ticketa
    cache_key = "stats:summary"

    cached_data = await get_cache(cache_key)

    if cached_data is not None:
        return TicketStatsResponse.model_validate(cached_data)

    stats = await get_ticket_stats(session)
    response = TicketStatsResponse(**stats)

    await set_cache(cache_key, response.model_dump(mode="json"))

    return response
