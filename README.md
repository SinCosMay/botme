# Float

Float is a Discord coding practice bot for competitive programming and interview prep.
It combines a Discord-first command experience, a FastAPI backend, and a lightweight web dashboard to help users practice consistently and track measurable progress.

## What Float Does

- Assigns Codeforces problems by mode: random, topic, or rating range.
- Verifies solves against Codeforces submissions after assignment time.
- Updates XP, rating, level, and streak automatically.
- Asks follow-up concept questions after verified solves.
- Tracks optional LeetCode company-wise practice separately.
- Shows live profile and leaderboard data in Discord.
- Exposes analytics APIs for dashboard charts and comparisons.

## Command Reference

| Command | Description |
|---|---|
| `/register <cf_handle>` | Link your Discord account to a Codeforces handle |
| `/problem [mode] [topic] [min_rating] [max_rating]` | Get a Codeforces assignment |
| `/solved` | Verify your latest active Codeforces assignment |
| `/followup <submission_id> <question_id> <answer>` | Submit follow-up answer for bonus XP |
| `/profile` | View your current progress profile |
| `/leaderboard [metric] [limit]` | View top users by XP or rating |
| `/lc_company <company> [topic] [difficulty]` | Get a LeetCode company-wise assignment |
| `/lc_solved <slug> [proof_url]` | Mark LeetCode assignment solved |
| `/help` | Show command overview |
| `/ping` | Show bot latency |

## Architecture

```text
Discord User
   |
   v
Discord Bot (slash commands)
   |
   v
FastAPI Backend
   |-- PostgreSQL (users, assignments, submissions, history)
   |-- Redis (cache and performance layer)
   |-- Codeforces API (verification + problem sync)
   |
   v
Frontend Dashboard (profile + leaderboard + charts)
```

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Alembic, Redis
- Bot: discord.py
- Frontend: Vite, vanilla JavaScript, Chart.js
- Database: PostgreSQL
- Testing: pytest

## Repository Layout

```text
backend/   FastAPI app, models, services, migrations, tests
bot/       Discord slash-command bot
frontend/  Dashboard application
scripts/   Data sync and import scripts
shared/    Shared constants and types
```

## Quick Start

### 1) Prerequisites

- Python 3.11+
- Node.js 18+
- Docker + Docker Compose
- Discord bot token

### 2) Configure Environment

```powershell
Copy-Item .env.example .env
Copy-Item backend/.env.example backend/.env
```

Required environment values:

- `DISCORD_TOKEN`
- `DATABASE_URL` (or `POSTGRES_*` values)
- `REDIS_URL`
- `API_URL`

### 3) Start Infrastructure

```powershell
docker compose up -d
```

### 4) Install Dependencies

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Push-Location frontend
npm install
Pop-Location
```

### 5) Apply Database Migrations

```powershell
Push-Location backend
alembic upgrade head
Pop-Location
```

### 6) Run Services

Backend:

```powershell
Push-Location backend
uvicorn app.main:app --reload --port 8000
```

Bot:

```powershell
python -m bot.main
```

Frontend:

```powershell
Push-Location frontend
npm run dev
```

## API Surface

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

## Data Utilities

Sync Codeforces problemset:

```powershell
python scripts/sync_codeforces.py --limit 3000
```

Import LeetCode company-wise data:

```powershell
python scripts/import_leetcode_company.py --input path/to/company_problems.json
```

## Testing

```powershell
Push-Location backend
pytest -q
```

## Contributing

Issues and pull requests are welcome.
For major changes, open an issue first so implementation details can be aligned before coding.
