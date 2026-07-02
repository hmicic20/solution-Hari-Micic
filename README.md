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

### 4. Sinkronizacija podataka iz DummyJSON-a

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

## API dokumentacija

FastAPI automatski generira dokumentaciju:

```text
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/redoc
```

## Konfiguracija

Primjer `.env` konfiguracije:

```env
APP_ENV=dev
APP_NAME=TicketHub
DATABASE_URL=sqlite+aiosqlite:///./tickethub.db
SYNC_ON_STARTUP=false
REDIS_URL=redis://localhost:6379/0
```

Za lokalni rad koristi se SQLite.

Za Docker Compose koristi se PostgreSQL:

```env
DATABASE_URL=postgresql+asyncpg://tickethub:tickethub@postgres:5432/tickethub
```

## Endpointi

### Health

```text
GET /health
```

Provjera radi li aplikacija i baza.

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
make docker-build
make docker-up
make docker-down
```

Na Windowsu se iste naredbe mogu pokrenuti i ručno ako `make` nije instaliran.

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
- Alembic migracije
- Docker build

Workflow se nalazi u:

```text
.github/workflows/ci.yml
```

## Vanjski izvor podataka

Podaci se dohvaćaju iz DummyJSON servisa:

```text
https://dummyjson.com/todos
https://dummyjson.com/users
```

Polja se mapiraju na lokalni Ticket model:

```text
todo -> title
completed=true -> closed
completed=false -> open
id % 3 -> low / medium / high
userId -> assignee username
```

Originalni JSON iz izvora sprema se u polje `source_payload`.

## Korištenje AI alata

Za izradu projekta korišten je ChatGPT kao pomoć pri:

- planiranju strukture projekta
- pisanju početnog koda
- objašnjavanju FastAPI, SQLAlchemy i Alembic dijelova
- pripremi testova
- pisanju README dokumentacije

Kod je ručno pregledan, pokrenut i testiran lokalno.