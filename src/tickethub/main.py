from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.database import get_db_session
from tickethub.routers.stats import router as stats_router
from tickethub.routers.tickets import router as tickets_router

app = FastAPI(
    title="TicketHub",
    description="Middleware REST service for syncing and managing support tickets.",
    version="0.1.0",
)

app.include_router(tickets_router)
app.include_router(stats_router)


@app.get("/health", tags=["health"])
async def health_check(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    # Provjera rade li API i baza
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Baza podataka nije dostupna.",
        ) from exc

    return {
        "status": "ok",
        "database": "ok",
    }
