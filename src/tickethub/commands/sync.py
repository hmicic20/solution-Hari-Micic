import asyncio

from tickethub.database import AsyncSessionLocal
from tickethub.services.sync_service import sync_tickets


async def main() -> None:
    # Ručno pokretanje sinkronizacije ticketa
    async with AsyncSessionLocal() as session:
        synced_count = await sync_tickets(session)

    print(f"Sinkronizirano ticketa: {synced_count}")


if __name__ == "__main__":
    asyncio.run(main())
