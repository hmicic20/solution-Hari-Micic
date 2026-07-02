from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.models import Ticket


async def get_ticket_stats(session: AsyncSession) -> dict[str, object]:
    # Računa osnovne statistike ticketa iz lokalne baze
    total_result = await session.execute(select(func.count()).select_from(Ticket))
    total = total_result.scalar_one()

    status_result = await session.execute(
        select(Ticket.status, func.count()).group_by(Ticket.status)
    )

    priority_result = await session.execute(
        select(Ticket.priority, func.count()).group_by(Ticket.priority)
    )

    by_status = {status: count for status, count in status_result.all()}

    by_priority = {priority: count for priority, count in priority_result.all()}

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
    }
