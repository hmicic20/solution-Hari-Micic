# TicketHub

TicketHub je FastAPI REST servis za dohvat support ticketa iz DummyJSON servisa i spremanje u lokalnu bazu podataka.

Aplikacija radi kao middleware servis: podaci se prvo sinkroniziraju iz vanjskog izvora, a zatim svi read i write endpointi rade nad lokalnom bazom.

## Tehnologije

- Python 3.11
- FastAPI
- Pydantic v2
- SQLAlchemy 2 async
- Alembic
- SQLite lokalno
- PostgreSQL u Docker Compose okruženju
- httpx
- pytest
- Ruff
- Redis
- Docker
- GitHub Actions

## Struktura projekta

```text
tickethub/
├── alembic/
├── docs/
├── src/
│   └── tickethub/
│       ├── clients/
│       ├── commands/
│       ├── repositories/
│       ├── routers/
│       ├── services/
│       ├── cache.py
│       ├── config.py
│       ├── database.py
│       ├── main.py
│       ├── mappers.py
│       ├── models.py
│       └── schemas.py
├── tests/
├── .github/workflows/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
└── README.md
```

## Lokalno pokretanje

### 1. Kreiranje virtualnog okruženja

```bash
py -3.11 -m venv .venv
```

Aktivacija na Windowsu:

```bash
.venv\Scripts\Activate.ps1
```

### 2. Instalacija dependencies

```bash
pip install -e ".[dev]"
```

### 3. Migracije baze

```bash
python -m alembic upgrade head
```

### 4. Sinkronizacija podataka

```bash
python -m tickethub.commands.sync
```

### 5. Pokretanje aplikacije

```bash
uvicorn tickethub.main:app --app-dir src --reload
```

Aplikacija je dostupna na:

```text
http://127.0.0.1:8000
```

## Konfiguracija

Primjer `.env` konfiguracije:

```env
APP_ENV=dev
APP_NAME=TicketHub
DATABASE_URL=sqlite+aiosqlite:///./tickethub.db

SYNC_ON_STARTUP=false

REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=false
CACHE_TTL_SECONDS=60

LOG_LEVEL=INFO
RATE_LIMIT_DEFAULT=100/minute

BACKGROUND_SYNC_ENABLED=false
BACKGROUND_SYNC_INTERVAL_SECONDS=300
```

Lokalno se koristi SQLite baza.

U Docker Compose okruženju koristi se PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://tickethub:tickethub@postgres:5432/tickethub
```

## API dokumentacija

FastAPI dokumentacija dostupna je nakon pokretanja aplikacije:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```

Statička OpenAPI/ReDoc dokumentacija može se generirati naredbom:

```bash
python -m tickethub.commands.export_openapi
```

Naredba generira:

```text
docs/openapi.json
docs/redoc.html
```

Statički ReDoc može se otvoriti direktno u browseru ili poslužiti lokalno:

```bash
python -m http.server 8080
```

Zatim otvoriti:

```text
http://127.0.0.1:8080/docs/redoc.html
```

## Endpointi

### Health

```text
GET /health
```

Provjerava radi li aplikacija i baza.

### Ticketi

```text
GET /tickets
GET /tickets/{id}
GET /tickets?status=open&priority=high
GET /tickets/search?q=test
POST /tickets
PATCH /tickets/{id}
```

### Statistika

```text
GET /stats
```

Vraća ukupan broj ticketa i grupiranje po statusu i prioritetu.

### Autentifikacija

```text
POST /auth/login
GET /auth/me
```

Primjer login zahtjeva:

```json
{
  "username": "emilys",
  "password": "emilyspass",
  "expires_in_mins": 30
}
```

`POST /auth/login` vraća `accessToken` i `refreshToken`.

Za `GET /auth/me` potrebno je poslati Bearer token kroz Swagger Authorize opciju ili kroz header:

```text
Authorization: Bearer <accessToken>
```

## Primjer kreiranja ticketa

```json
{
  "title": "Problem s prijavom",
  "description": "Korisnik se ne može prijaviti u sustav.",
  "status": "open",
  "priority": "medium",
  "assignee": "marko"
}
```

## Primjer izmjene ticketa

```json
{
  "status": "closed",
  "priority": "high"
}
```

## Vanjski izvor podataka

Podaci se dohvaćaju iz DummyJSON servisa:

```text
https://dummyjson.com/todos
https://dummyjson.com/users
```

Kod sinkronizacije se eksplicitno dohvaćaju svi dostupni zapisi iz DummyJSON servisa, pa ukupan broj ticketa ovisi o trenutačnom broju podataka koje DummyJSON vraća.

Mapiranje podataka:

```text
todo -> title
completed=true -> closed
completed=false -> open
id % 3 -> low / medium / high
userId -> assignee username
```

Originalni JSON iz izvora sprema se u polje `source_payload`.

## Dodatne funkcionalnosti

### Redis cache

Redis cache se koristi za read endpoint-e:

```text
GET /tickets
GET /tickets/search
GET /stats
```

Cache se briše kod:

```text
POST /tickets
PATCH /tickets/{id}
```

Lokalno je cache isključen po defaultu, a može se uključiti kroz:

```env
CACHE_ENABLED=true
CACHE_TTL_SECONDS=60
```

### Rate limiting

API koristi rate limiting preko SlowAPI paketa.

Primjeri limita:

```text
/tickets endpointi: 60/minute
/auth/login: 10/minute
default: 100/minute
```

Konfiguracija:

```env
RATE_LIMIT_DEFAULT=100/minute
```

### Logiranje

Aplikacija koristi osnovno logiranje za važne događaje u sustavu:

```text
INFO - normalan rad aplikacije, sync i dohvat podataka
WARNING - problemi s cacheom ili vanjskim servisima
ERROR - greške kod health-checka ili neočekivane greške
```

Razina logiranja podešava se kroz varijablu:

```env
LOG_LEVEL=INFO
```

### Background sync

Projekt podržava opcionalni background sync job koji periodično dohvaća podatke iz DummyJSON-a.

Po defaultu je isključen:

```env
BACKGROUND_SYNC_ENABLED=false
BACKGROUND_SYNC_INTERVAL_SECONDS=300
```

Background sync ne prepisuje postojeće lokalno izmijenjene tickete, kako se ručne izmjene napravljene preko `PATCH /tickets/{id}` ne bi izgubile.

### Integritet baze

Baza koristi Alembic migracije za verzioniranje sheme.

Za `status` i `priority` dodani su DB constrainti kako bi baza prihvaćala samo dopuštene vrijednosti:

```text
status: open / closed
priority: low / medium / high
```

Kod sinkronizacije s DummyJSON-om koriste se izvorni ID-jevi ticketa. Nakon synca u PostgreSQL okruženju aplikacija usklađuje ID sequence kako bi novi ticketi kreirani preko `POST /tickets` dobili ispravan sljedeći ID.

## Docker pokretanje

```bash
docker compose up --build
```

Docker Compose pokreće:

- API servis
- PostgreSQL bazu
- Redis servis

Kod pokretanja containera izvršavaju se migracije i sinkronizacija podataka.

Gašenje:

```bash
docker compose down
```

Gašenje i brisanje volumena baze:

```bash
docker compose down -v
```

## Makefile naredbe

```bash
make install
make run
make test
make lint
make format
make migrate
make sync
make docs
make docker-build
make docker-up
make docker-down
```

Na Windowsu se iste naredbe mogu pokrenuti ručno ako `make` nije instaliran.

## Testiranje

```bash
pytest
```

## Lint i formatiranje

```bash
ruff check src tests
ruff format src tests
```

## CI

Projekt koristi GitHub Actions workflow koji pokreće:

- instalaciju dependencies
- Ruff lint
- pytest testove
- generiranje statičke OpenAPI/ReDoc dokumentacije
- Alembic migracije
- Docker build

Workflow se nalazi u:

```text
.github/workflows/ci.yml
```

## Korištenje AI alata

Za izradu projekta korišten je ChatGPT kao pomoć pri:

- planiranju strukture projekta
- pisanju početnog koda
- objašnjavanju FastAPI, SQLAlchemy i Alembic dijelova
- pripremi testova
- pisanju README dokumentacije

Kod je ručno pregledan, pokrenut i testiran lokalno.

Projekt je lokalno testiran kroz pytest, Ruff, Alembic migracije, Docker Compose okruženje i ručnu provjeru endpointa kroz Swagger dokumentaciju.