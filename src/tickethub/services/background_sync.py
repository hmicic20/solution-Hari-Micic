import asyncio
import logging

from tickethub.config import settings
from tickethub.database import AsyncSessionLocal
from tickethub.services.sync_service import sync_tickets

logger = logging.getLogger(__name__)


async def run_single_sync() -> None:
    # Pokreće jednu sinkronizaciju ticketa
    try:
        async with AsyncSessionLocal() as session:
            synced_count = await sync_tickets(
                session=session,
                overwrite_existing=False,
            )

        logger.info("Background sync završen. Broj ticketa: %s", synced_count)
    except Exception:
        logger.exception("Background sync nije uspio.")


async def run_background_sync_loop() -> None:
    # Periodično pokreće sinkronizaciju dok aplikacija radi
    logger.info(
        "Background sync pokrenut. Interval: %s sekundi.",
        settings.background_sync_interval_seconds,
    )

    while True:
        await asyncio.sleep(settings.background_sync_interval_seconds)
        await run_single_sync()
