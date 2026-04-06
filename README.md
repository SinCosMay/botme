# BotMe

BotMe is a Discord-first coding practice bot with a FastAPI backend and a lightweight web dashboard.
It helps users practice Codeforces consistently, track progress, compete on leaderboards, and run an optional LeetCode company-wise practice flow.

## Highlights

- Slash-command workflow for daily problem solving.
- Automatic Codeforces solve verification against assignment time.
- XP, level, rating, and streak progression.
- Follow-up concept questions after verified solves.
- Leaderboard and profile views in Discord.
- Optional LeetCode company-wise assignment and solve tracking.
- REST API + test suite + Dockerized local Postgres/Redis.

## Core User Experience

1. Register your Codeforces handle from Discord.
2. Request a problem (random, by topic, or by rating range).
3. Submit `/solved` when done.
4. Bot verifies accepted submission through Codeforces API.
5. XP/rating/streak update and a follow-up question is generated.
6. View progress using `/profile` and `/leaderboard`.

## Discord Commands

| Command | Purpose |
|---|---|
| `/register <cf_handle>` | Link Discord account to Codeforces handle |
| `/problem [mode] [topic] [min_rating] [max_rating]` | Assign a Codeforces problem |
| `/solved` | Verify latest active Codeforces assignment |
| `/followup <submission_id> <question_id> <answer>` | Submit follow-up answer for bonus XP |
| `/profile` | Show your current profile stats |
| `/leaderboard [metric] [limit]` | Show ranking by XP or rating |
| `/lc_company <company> [topic] [difficulty]` | Assign a LeetCode problem by company |
| `/lc_solved <slug> [proof_url]` | Mark assigned LeetCode problem solved |

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Alembic, Redis
- Bot: discord.py
- Frontend: Vite + vanilla JS + Chart.js
- Database: PostgreSQL
- Tests: pytest

## Repository Layout

```text
backend/   FastAPI app, services, models, migrations, tests
bot/       Discord slash command bot
frontend/  Dashboard app (home, leaderboard, profile)
scripts/   Data sync/import scripts
shared/    Shared enums/constants/types
```

## Quick Start (Local)

### 1) Prerequisites

- Python 3.11+
- Node.js 18+
- Docker + Docker Compose
- A Discord bot token

### 2) Environment

Copy and edit environment variables:

```powershell
Copy-Item .env.example .env
Copy-Item backend/.env.example backend/.env
```

Minimum required values in `.env`:

- `DISCORD_TOKEN`
- `DATABASE_URL` (or `POSTGRES_*` vars)
- `REDIS_URL`
- `API_URL`

### 3) Start infrastructure

```powershell
docker compose up -d
```

### 4) Install dependencies

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Push-Location frontend
npm install
Pop-Location
```

### 5) Run migrations

```powershell
Push-Location backend
alembic upgrade head
Pop-Location
```

### 6) Run services

Terminal A (backend):

```powershell
Push-Location backend
uvicorn app.main:app --reload --port 8000
```

Terminal B (bot):

```powershell
python -m bot.main
```

Terminal C (frontend):

```powershell
Push-Location frontend
npm run dev
```

## API Overview

- `GET /v1/health`
- `GET /v1/ready`
- `GET /v1/metrics`
- `POST /v1/users/register`
- `GET /v1/users/{discord_id}/profile`
- `GET /v1/users/handle/{cf_handle}/profile`
- `POST /v1/problems/assign`
- `POST /v1/problems/assign/leetcode`
- `POST /v1/submissions/verify`
- `POST /v1/submissions/leetcode/mark-solved`
- `POST /v1/followup/answer`
- `GET /v1/analytics/leaderboard`
- `GET /v1/analytics/{user_id}`
- `GET /v1/analytics/{user_id}/timeseries`
- `POST /v1/leetcode/import/company-problems`
- `POST /v1/leetcode/assign`

## Data Operations

Sync Codeforces problems:

```powershell
python scripts/sync_codeforces.py --limit 3000
```

Import LeetCode company-wise dataset:

```powershell
python scripts/import_leetcode_company.py --input path/to/company_problems.json
```

## Testing

Run full backend tests:

```powershell
Push-Location backend
pytest -q
```

## Status

### Implemented

- User registration and Codeforces handle validation.
- Codeforces assignment modes (random/topic/rating).
- Codeforces solve verification and duplicate protection.
- XP/rating/level/streak updates with history tracking.
- Follow-up question generation and answer scoring.
- Analytics leaderboard with Redis caching.
- Discord slash command integration for the core flow.
- Optional LeetCode company-wise assignment and solve tracking.
- Basic dashboard pages for home, leaderboard, and profile.
- Observability endpoints (`/v1/metrics`) and request tracing.

### Pending / In Progress

- Rich embed formatting for commands beyond profile and leaderboard.
- Expanded dashboard UX and deeper analytics visualizations.
- Stronger production hardening (rate limits, retries, deployment templates).
- Extended command modules (help, streak, lc_profile) wired into slash tree.

## Contributing

Issues and pull requests are welcome.
For major feature changes, open an issue first so implementation details can be aligned before coding.

## License

No license file is currently declared in this repository.
Add a license before publishing or accepting broad external contributions.
