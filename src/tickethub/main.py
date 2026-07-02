import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress

from fastapi import Depends, FastAPI, HTTPException, status
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from tickethub.config import settings
from tickethub.database import get_db_session
from tickethub.logging_config import configure_logging
from tickethub.rate_limit import limiter
from tickethub.routers.auth import router as auth_router
from tickethub.routers.stats import router as stats_router
from tickethub.routers.tickets import router as tickets_router
from tickethub.services.background_sync import (
    run_background_sync_loop,
    run_single_sync,
)

configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Pokreće opcionalni sync kod starta aplikacije
    background_task: asyncio.Task[None] | None = None

    if settings.sync_on_startup:
        await run_single_sync()

    if settings.background_sync_enabled:
        background_task = asyncio.create_task(run_background_sync_loop())

    try:
        yield
    finally:
        if background_task is not None:
            background_task.cancel()

            with suppress(asyncio.CancelledError):
                await background_task


app = FastAPI(
    title="TicketHub",
    description="Middleware REST service for syncing and managing support tickets.",
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(tickets_router)
app.include_router(stats_router)
app.include_router(auth_router)


@app.get("/health", tags=["health"])
async def health_check(
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    # Provjera rade li API i baza
    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.error("Provjera baze nije uspjela.", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Baza podataka nije dostupna.",
        ) from exc

    return {
        "status": "ok",
        "database": "ok",
    }
