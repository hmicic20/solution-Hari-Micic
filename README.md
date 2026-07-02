# TicketHub

TicketHub je FastAPI REST servis za dohvat support ticketa iz DummyJSON servisa i spremanje u lokalnu bazu podataka.

## Trenutno stanje

Projekt trenutno ima osnovnu FastAPI strukturu i health-check endpoint.

## Lokalno pokretanje

```bash
uvicorn tickethub.main:app --app-dir src --reload