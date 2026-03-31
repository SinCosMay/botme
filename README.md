# BotMe: Codeforces Practice Tracker

A full-stack project where users solve Codeforces problems through Discord, and your system verifies solves, awards XP, updates rating/streak, and visualizes progress on a web dashboard.

This README is a practical implementation guide and a living roadmap. We will execute it phase-by-phase and keep it updated.

## 1) Project Goal

Build a production-style learning system with three layers:
- Discord Bot: interaction layer (commands, prompts, reminders)
- Backend Server: core logic (verification, XP, rating, analytics)
- Web Dashboard: visualization (profile, graphs, leaderboard)

What this demonstrates on a resume:
- Backend architecture and API design
- Third-party API integration (Codeforces)
- Async background jobs
- Caching with Redis
- Data modeling + analytics pipelines
- Full-stack integration

## 2) Current Repository Structure

```text
botme/
  api/
  backend/
    app/
      main.py
  bot/
  scripts/
  shared/
  docker-compose.yml
  requirements.txt
```

Current notes:
- Docker services exist for Postgres and Redis in `docker-compose.yml`.
- `backend/app/main.py` currently contains sample CRUD logic (campaign demo), not final project domain logic.

## 3) System Architecture (Target)

```text
Discord User
   |
   v
Discord Bot (commands, follow-up Q&A)
   |
   | REST/WebSocket
   v
Backend API (FastAPI)
   |           |
   |           +--> Redis (cache + queues + short-lived state)
   |
   +--> Postgres (users, problems, solves, xp, rating history, streaks, follow-ups)
   |
   +--> Codeforces API (problemset, user submissions)
   |
   +--> Background Workers (daily challenge, streak reset, leaderboard refresh)

Web Dashboard (Next.js/React) <---- Backend API
```

## 4) End-to-End User Flow (Implemented Behavior)

1. User joins via Discord command.
2. Bot links Discord ID to Codeforces handle.
3. User requests a problem.
4. System picks a filtered Codeforces problem and sends metadata.
5. User submits "I solved it".
6. Backend verifies accepted solve via Codeforces API.
7. If valid and not duplicate, backend awards XP and updates rating/streak/history.
8. Bot asks follow-up concept question.
9. User answers; backend validates and awards bonus XP.
10. User views profile in bot or web dashboard.
11. Background jobs keep challenges, streaks, and leaderboard fresh.

## 5) Domain Model (MVP Tables)

Use Postgres for persistence.

- users
  - id (uuid, pk)
  - discord_id (text, unique, not null)
  - cf_handle (text, unique, not null)
  - xp (int, default 0)
  - rating (int, default 1000)
  - level (int, default 1)
  - current_streak (int, default 0)
  - longest_streak (int, default 0)
  - last_solved_at (timestamptz, nullable)
  - created_at, updated_at

- problems
  - id (uuid, pk)
  - cf_contest_id (int)
  - cf_index (text)
  - name (text)
  - rating (int, nullable)
  - tags (jsonb)
  - url (text)
  - source_last_seen_at (timestamptz)
  - unique (cf_contest_id, cf_index)

- assignments
  - id (uuid, pk)
  - user_id (fk users)
  - problem_id (fk problems)
  - assigned_at (timestamptz)
  - status (enum: assigned, solved, expired)

- submissions
  - id (uuid, pk)
  - user_id (fk users)
  - problem_id (fk problems)
  - cf_submission_id (bigint, unique)
  - verdict (text)
  - solved_at (timestamptz)
  - xp_awarded (int)
  - bonus_xp_awarded (int, default 0)

- followup_questions
  - id (uuid, pk)
  - problem_id (fk problems)
  - question_type (enum: complexity, key_idea, concept)
  - prompt (text)
  - expected_answer (text/jsonb)
  - bonus_xp (int)

- followup_attempts
  - id (uuid, pk)
  - submission_id (fk submissions)
  - user_answer (text)
  - is_correct (bool)
  - awarded_xp (int)
  - attempted_at (timestamptz)

- rating_history
  - id (uuid, pk)
  - user_id (fk users)
  - old_rating (int)
  - new_rating (int)
  - reason (text)
  - created_at (timestamptz)

- xp_history
  - id (uuid, pk)
  - user_id (fk users)
  - amount (int)
  - source (text)
  - metadata (jsonb)
  - created_at (timestamptz)

- daily_user_stats (optional, for analytics speed)
  - day (date)
  - user_id (fk users)
  - solved_count (int)
  - xp_gained (int)
  - primary key (day, user_id)

## 6) Core Formulas (Initial Version)

Keep formulas simple first, then tune.

Base XP by problem rating:
- If rating is known: `base_xp = max(20, floor(rating / 40))`
- If rating unknown: `base_xp = 25`

First-time solve bonus:
- `+10` XP if this is user's first accepted solve at that rating bucket (optional in V2)

Follow-up bonus:
- Correct follow-up answer: `+5` to `+20` XP (question difficulty based)

Custom rating update:
- `delta = clamp((problem_rating - user_rating) / 80, -15, +30)`
- Accepted solve gives `rating += round(10 + delta)`
- Follow-up correct can add small `+2` rating (optional)

Leveling:
- `level = floor(sqrt(xp / 100)) + 1`

Streak:
- Increment if solved on consecutive UTC dates
- Reset to 0 when a day is missed (handled by daily job)

## 7) API Surface (MVP)

Backend routes (suggested):
- `POST /v1/users/register` -> map Discord ID to CF handle
- `GET /v1/users/{discord_id}/profile`
- `POST /v1/problems/assign` -> get next recommended problem
- `POST /v1/submissions/verify` -> verify solve with CF API
- `POST /v1/followup/answer` -> validate answer, award bonus XP
- `GET /v1/leaderboard?metric=xp|rating&limit=50`
- `GET /v1/analytics/{user_id}` -> charts payload

Codeforces integration routes/services:
- pull + sync problemset metadata
- fetch submissions by CF handle
- verify `OK` verdict for contest+index after assignment timestamp

## 8) Discord Bot Commands (MVP)

- `/register <cf_handle>`
- `/problem [rating] [tag]`
- `/solved` (verifies latest active assignment)
- `/profile`
- `/leaderboard`
- `/streak`
- `/help`

Bot behavior:
- On `/solved`, verify solve before rewards.
- If accepted, immediately trigger follow-up question.
- For retries/invalid solves, return clear reason.

## 9) Web Dashboard (MVP Pages)

- `/profile/:handle`
  - XP, rating, level, streak, solved count
  - rating-over-time chart
  - solved-by-tag chart
  - difficulty distribution chart

- `/leaderboard`
  - rank by XP/rating
  - user comparison cards

- `/challenges` (optional V2)
  - daily challenge and status

## 10) Caching + Background Jobs

Redis usage:
- cache Codeforces problemset (TTL 6h)
- cache user submissions short-term (TTL 2-5m)
- temporary bot interaction state (pending follow-up question)

Background jobs:
- daily at 00:05 UTC: streak reset checks + daily challenge generation
- every 10 min: leaderboard materialized refresh/cache warm
- every 6h: Codeforces problemset sync

Suggested tooling:
- Celery/RQ/Arq + Redis queue
- APScheduler for simple scheduler start (if avoiding full worker initially)

## 11) Implementation Phases (Build Order)

### Phase 0 - Foundation and Cleanup
Goal: establish project baseline and remove demo code.

Tasks:
- Define folder ownership (`backend`, `bot`, `api`, `shared`).
- Replace campaign demo models/routes in backend with project domain scaffold.
- Add env management (`.env.example`) and config loader.
- Add migration tooling (Alembic).
- Add lint/format/test setup.

Exit criteria:
- Backend starts successfully with health endpoint.
- Postgres + Redis connected from app.
- One migration runs cleanly.

### Phase 1 - User + Problem + Codeforces Integration
Goal: user registration and problem assignment working end-to-end.

Tasks:
- Implement user registration (Discord ID <-> CF handle).
- Implement Codeforces handle verification.
- Build problemset sync service from Codeforces API.
- Implement problem filtering and random assignment.
- Persist assignments.

Exit criteria:
- `/register` and `/problem` bot commands work with backend.
- Assigned problem stored and retrievable.

### Phase 2 - Solve Verification + Progress Engine
Goal: core logic correctness.

Tasks:
- Verify accepted solve from CF submissions.
- Prevent duplicate rewards.
- Award XP and update level.
- Update rating and rating history.
- Update streak and solved counters.

Exit criteria:
- `/solved` updates all profile fields correctly.
- Duplicate solve attempt yields no extra XP.

### Phase 3 - Follow-up Question Engine
Goal: add unique learning feature.

Tasks:
- Create follow-up question templates by tag/rating.
- Ask follow-up after solve confirmation.
- Validate answer (exact/keyword/rubric approach).
- Award bonus XP and store attempts.

Exit criteria:
- Users get immediate follow-up prompt after accepted solve.
- Bonus XP tracked and visible in profile history.

### Phase 4 - Leaderboard + Analytics API
Goal: make insights available.

Tasks:
- Build leaderboard query endpoints.
- Build analytics aggregations.
- Add time-series endpoints for charts.
- Add Redis caching for expensive queries.

Exit criteria:
- Leaderboard endpoint supports rank + pagination.
- Analytics endpoint returns chart-ready data.

### Phase 5 - Web Dashboard
Goal: visual product layer complete.

Tasks:
- Build profile and leaderboard pages.
- Integrate chart components.
- Connect to backend APIs.
- Add loading/error states.

Exit criteria:
- User can inspect progress visually without Discord.

### Phase 6 - Production Readiness
Goal: quality and reliability.

Tasks:
- Add integration tests for core flows.
- Add background jobs for daily tasks.
- Add observability (structured logs, metrics basics).
- Dockerize services for local full run.

Exit criteria:
- Stable end-to-end demo for portfolio.
- Readme and architecture docs updated.

## 12) Learning Plan (Resume-Oriented)

Target skills by phase:
- Phase 0: FastAPI architecture, config patterns, migrations
- Phase 1: external API integration + data modeling
- Phase 2: domain logic correctness + idempotency
- Phase 3: product thinking (learning loop design)
- Phase 4: analytics modeling + cache strategy
- Phase 5: frontend data visualization + API consumption
- Phase 6: reliability engineering + deployment practices

How to show learning in commits:
- one feature per commit (clear message)
- include tests for every core logic unit
- document tradeoffs in PR/commit notes

## 13) Progress Tracker (Update This Weekly)

Use this section as the single source of truth.

### Status Board

- [ ] Phase 0 complete
- [ ] Phase 1 complete
- [ ] Phase 2 complete
- [ ] Phase 3 complete
- [ ] Phase 4 complete
- [ ] Phase 5 complete
- [ ] Phase 6 complete

### Current Sprint

- Sprint goal: Phase 0 foundation
- Start date: 2026-04-01
- End date: TBD

Planned tasks:
- [ ] Replace backend campaign demo with domain skeleton
- [ ] Add SQLAlchemy models for users/problems/submissions
- [ ] Add Alembic setup and first migration
- [ ] Add basic health + readiness endpoints
- [ ] Add env config and `.env.example`

### Changelog

- 2026-04-01: Initial roadmap README created.

## 14) Suggested Milestone Branch Strategy

- `main`: stable milestones only
- `phase-0-foundation`
- `phase-1-integration`
- `phase-2-progress-engine`
- `phase-3-followup`
- `phase-4-analytics`
- `phase-5-dashboard`
- `phase-6-prod-readiness`

## 15) Immediate Next Step (What We Should Build Next)

Start with Phase 0 in this order:
1. Replace backend demo (`campaign`) with domain modules (`users`, `problems`, `submissions`, `progress`).
2. Switch backend DB from local sqlite demo to Postgres via env config.
3. Add migrations.
4. Add basic tests for registration and assignment services.

Once Phase 0 is done, we move to Phase 1 and keep this README updated after each milestone.
