from fastapi import FastAPI

from tickethub.routers.tickets import router as tickets_router


app = FastAPI(
    title="TicketHub",
    description="Middleware REST service for syncing and managing support tickets.",
    version="0.1.0",
)

app.include_router(tickets_router)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    # Provjera radi li servis
    return {"status": "ok"}