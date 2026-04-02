# BotMe

BotMe is a practice automation platform for competitive programming workflows.
It combines a FastAPI backend, a Discord bot, and a Vite frontend to support:

- user registration and profile tracking
- problem assignment and verification
- follow-up question workflows
- analytics and leaderboard views

## Architecture

- `backend/`: FastAPI application, SQLAlchemy models, Alembic migrations, background jobs, and test suite
- `bot/`: Discord bot commands and backend client integration
- `frontend/`: Vite dashboard for profile, leaderboard, and home views
- `scripts/`: operational scripts for external platform synchronization

## Technology Stack

- Python 3.11+ (FastAPI, SQLAlchemy, Alembic, discord.py)
- PostgreSQL for persistence
- Redis for caching and scheduling support
- Node.js + Vite for frontend development
- Docker Compose for local infrastructure

## Quick Start (Development)

### 1. Prerequisites

- Python 3.11+
- Node.js 18+
- Docker Desktop (recommended for local Postgres/Redis)

### 2. Environment Setup

```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` from your template and configure the required values:

- `DATABASE_URL` (or `POSTGRES_*` variables)
- `REDIS_URL`
- `DISCORD_TOKEN`
- `API_URL`

### 3. Start Infrastructure

```powershell
docker compose up -d
```

### 4. Run Migrations

```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

### 5. Start Services

Backend:

```powershell
python -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

Frontend:

```powershell
cd frontend
npm install
npm run dev
```

Discord bot:

```powershell
cd ..
python -m bot.main
```

## Common Operations

Sync Codeforces problemset:

```powershell
curl -X POST http://127.0.0.1:8000/v1/problems/sync/codeforces
```

Run backend tests:

```powershell
python -m pytest backend/tests -q
```

## Bot Command Summary

- `/register <cf_handle>`: link Discord account to Codeforces handle
- `/problem ...`: request a new assignment using filters
- `/solved`: verify latest assignment completion
- `/followup <submission_id> <question_id> <answer>`: submit follow-up response
- `/lc_company`, `/lc_solved`: LeetCode workflows

## Security and Vulnerability Status

Last checked: 2026-04-02

- Frontend production dependencies (`npm audit --omit=dev`): 0 vulnerabilities
- Python dependencies (`pip-audit`): vulnerabilities detected in transitive package `aiohttp` and local tooling `pip`

Mitigation applied in this repository:

- pinned `aiohttp==3.13.4` in `requirements.txt` to address CVEs affecting `3.13.3`

Recommended cadence:

- run `pip-audit` and `npm audit --omit=dev` in CI on every pull request
- schedule a weekly dependency review for both Python and Node ecosystems
- keep build-time tooling (`pip`) updated in development and CI runners

## Deployment Guidance

- deploy backend and bot as separate processes/services
- use managed PostgreSQL and Redis with backups enabled
- put backend behind TLS termination (reverse proxy or API gateway)
- configure structured logging and monitoring dashboards
- store secrets in a secret manager, not in source control

## Contributing

- submit focused pull requests with tests for behavior changes
- include migration scripts for schema-affecting updates
- avoid committing `.env`, API keys, tokens, or credential files

## License

MIT
