# BotMe: Codeforces Practice Tracker (+ Optional LeetCode Company-Wise Track)

A full-stack project where users solve Codeforces problems through Discord, and your system verifies solves, awards XP, updates rating/streak, and visualizes progress on a web dashboard.

Extension supported: users can also practice LeetCode company-wise questions as a separate track for preparation and analytics.

This README is a practical implementation guide and a living roadmap. We will execute it phase-by-phase and keep it updated.

## 1) Project Goal

Build a production-style learning system with three layers:
- Discord Bot: interaction layer (commands, prompts, reminders)
- Backend Server: core logic (verification, XP, rating, analytics)
- Web Dashboard: visualization (profile, graphs, leaderboard)

Platform scope:
- Primary competitive track: Codeforces (verified, score-impacting) with random, topic-wise, and rating-wise assignment
- Optional interview track: LeetCode company-wise only (separate progress counters by default)

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
  backend/
    app/
      main.py
      api/v1/
      core/
      models/
      schemas/
      services/
    alembic/
    tests/
  bot/
    main.py
    commands/
    services/
  scripts/
  shared/
  docker-compose.yml
  requirements.txt
```

Current notes:
- Docker services exist for Postgres and Redis in `docker-compose.yml`.
- FastAPI app now runs domain routes via `v1` router (`users`, `problems`, `submissions`, `analytics`, `leetcode`, `health`).
- Alembic migration includes `users`, `problems`, `assignments`, `submissions`, and `user_platform_stats`.
- Codeforces sync + verification services are implemented (`problemset.problems`, `user.info`, `user.status`).
- Bot slash commands are wired for register, problem assignment, solve verification, profile, and LeetCode company flow.

## 3) Current Progress Snapshot (As Of 2026-04-02)

Completed now:
- [x] Replaced demo API surface with domain API routes under `/v1`.
- [x] Implemented registration, assignment, analytics, and submission endpoints.
- [x] Added Codeforces services for handle verification, problemset sync, and assignment solve verification.
- [x] Added LeetCode company dataset import + assignment + mark-solved flow.
- [x] Added Phase 2 core solve logic: duplicate protection, XP/rating update, level recompute, and streak progression.
- [x] Added backend tests for registration, assignment, LeetCode track, and Phase 2 verification service behavior.

Not completed yet:
- [ ] Add `rating_history` and `xp_history` tables + write paths.
- [ ] Add leaderboard endpoint and ranking queries.
- [ ] Add follow-up question engine and bonus XP flow.
- [ ] Add scheduled jobs for streak reset, challenge creation, and cache warming.

## 4) System Architecture (Target)

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

Additional data source for interview prep:
- GitHub dataset for LeetCode company-wise mapping:
  - https://github.com/liquidslr/leetcode-company-wise-problems
  - Use as metadata source (company -> problem slug/title/url/tags/difficulty)

## 5) End-to-End User Flow (Target Behavior)

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

Optional LeetCode flow (separate track):
1. User asks for company-wise practice (example: Google medium).
2. System selects LeetCode problem from imported company-wise dataset.
3. User marks it solved.
4. System records solve in LeetCode track counters.
5. By default, this does not change Codeforces XP/rating/streak.

## 6) Domain Model (MVP Tables)

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
  - platform (enum: codeforces, leetcode)
  - cf_contest_id (int)
  - cf_index (text)
  - lc_problem_id (text, nullable)
  - lc_slug (text, nullable)
  - name (text)
  - rating (int, nullable)
  - tags (jsonb)
  - url (text)
  - companies (jsonb, nullable)
  - source_last_seen_at (timestamptz)
  - unique (platform, cf_contest_id, cf_index)
  - unique (platform, lc_slug)

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
  - platform (enum: codeforces, leetcode)
  - cf_submission_id (bigint, unique)
  - proof_url (text, nullable)
  - verdict (text)
  - solved_at (timestamptz)
  - xp_awarded (int)
  - bonus_xp_awarded (int, default 0)
  - unique (user_id, problem_id)

- user_platform_stats (recommended)
  - user_id (fk users)
  - platform (enum: codeforces, leetcode)
  - solved_count (int, default 0)
  - streak (int, default 0)
  - last_solved_at (timestamptz, nullable)
  - xp (int, default 0)
  - rating (int, nullable)
  - primary key (user_id, platform)

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

## 7) Core Formulas (Initial Version)

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

LeetCode track default policy:
- LeetCode solved count contributes to LeetCode analytics only.
- Codeforces XP/rating/streak remain unchanged.
- Optional flag later: enable global XP for LeetCode with reduced weights.

## 8) API Surface (MVP)

Backend routes (suggested):
- `POST /v1/users/register` -> map Discord ID to CF handle
- `GET /v1/users/{discord_id}/profile`
- `POST /v1/problems/assign` -> get next recommended problem
- `POST /v1/submissions/verify` -> verify solve with CF API
- `POST /v1/followup/answer` -> validate answer, award bonus XP
- `GET /v1/leaderboard?metric=xp|rating&limit=50`
- `GET /v1/analytics/{user_id}` -> charts payload

LeetCode company-wise routes (new):
- `POST /v1/leetcode/import/company-problems` -> import/update dataset
- `POST /v1/problems/assign/leetcode` -> assign by company (optional difficulty filter)
- `POST /v1/submissions/leetcode/mark-solved` -> record solved (self-report mode)
- `GET /v1/analytics/{user_id}?platform=leetcode` -> LC-only analytics

Codeforces integration routes/services:
- pull + sync problemset metadata
- fetch submissions by CF handle
- verify `OK` verdict for contest+index after assignment timestamp

Codeforces API auth note:
- Current endpoints used (`problemset.problems`, `user.info`, `user.status`) work without API keys.
- API key/secret is optional unless you later use signed endpoints or need stricter rate-limit handling.

LeetCode integration note:
- No official public LeetCode API equivalent to CF verification.
- Implement V1 as tracked practice mode:
  - self-reported solved events + duplicate protection
  - optional proof URL (submission screenshot or profile link)
  - optional review queue for strict mode

## 9) Discord Bot Commands (MVP)

- `/register <cf_handle>`
- `/problem random`
- `/problem topic <tag>`
- `/problem rating <min_rating> <max_rating>`
- `/solved` (verifies latest active assignment)
- `/profile`
- `/leaderboard`
- `/streak`
- `/help`

LeetCode company-wise commands (new):
- `/lc_company <company> [difficulty]`
- `/lc_solved`
- `/lc_profile`

Bot behavior:
- On `/solved`, verify solve before rewards.
- If accepted, immediately trigger follow-up question.
- For retries/invalid solves, return clear reason.
- For `/lc_solved`, record solve in LeetCode track (no CF score impact by default).

## 10) Web Dashboard (MVP Pages)

- `/profile/:handle`
  - XP, rating, level, streak, solved count
  - rating-over-time chart
  - solved-by-tag chart
  - difficulty distribution chart

- `/leaderboard`
  - rank by XP/rating
  - user comparison cards

- `/leetcode`
  - company-wise solved progress
  - difficulty split
  - top companies practiced

- `/challenges` (optional V2)
  - daily challenge and status

## 11) Caching + Background Jobs

Redis usage:
- cache Codeforces problemset (TTL 6h)
- cache user submissions short-term (TTL 2-5m)
- temporary bot interaction state (pending follow-up question)

Background jobs:
- daily at 00:05 UTC: streak reset checks + daily challenge generation
- every 10 min: leaderboard materialized refresh/cache warm
- every 6h: Codeforces problemset sync
- daily/weekly: refresh LeetCode company-wise dataset snapshot

Suggested tooling:
- Celery/RQ/Arq + Redis queue
- APScheduler for simple scheduler start (if avoiding full worker initially)

## 12) Implementation Phases (Build Order)

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
- Implement problem assignment modes: random, topic-wise, rating-wise.
- Persist assignments.

Exit criteria:
- `/register` and `/problem` bot commands work with backend.
- Assigned problem stored and retrievable.

### Phase 1.5 - LeetCode Company-Wise Dataset + Separate Track
Goal: add interview-practice track without disturbing CF scoring logic.

Tasks:
- Build importer from the GitHub company-wise dataset into `problems` where platform=leetcode.
- Add company-wise assignment for LeetCode (optional difficulty filter only).
- Add `user_platform_stats` and LeetCode solve recording endpoint.
- Keep XP/rating impact disabled for LeetCode by default.

Exit criteria:
- `/lc_company` and `/lc_solved` work end-to-end.
- LeetCode solves appear in analytics but CF XP/rating do not change.

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

## 13) Learning Plan (Resume-Oriented)

Target skills by phase:
- Phase 0: FastAPI architecture, config patterns, migrations
- Phase 1: external API integration + data modeling
- Phase 1.5: dataset ingestion pipelines + multi-platform domain design
- Phase 2: domain logic correctness + idempotency
- Phase 3: product thinking (learning loop design)
- Phase 4: analytics modeling + cache strategy
- Phase 5: frontend data visualization + API consumption
- Phase 6: reliability engineering + deployment practices

How to show learning in commits:
- one feature per commit (clear message)
- include tests for every core logic unit
- document tradeoffs in PR/commit notes

## 14) Progress Tracker (Update This Weekly)

Use this section as the single source of truth.

### Status Board

- [x] Phase 0 complete
- [x] Phase 1 complete
- [x] Phase 1.5 complete
- [x] Phase 2 complete
- [~] Phase 3 in progress
- [~] Phase 4 in progress
- [ ] Phase 5 complete
- [ ] Phase 6 complete

### Current Sprint

- Sprint goal: Phase 4 analytics and leaderboard
- Start date: 2026-04-02
- End date: TBD

Planned tasks:
- [x] Add leaderboard endpoint with rank and pagination
- [x] Add time-series analytics endpoint for XP and rating
- [x] Add Redis-backed caching for leaderboard and time-series payloads
- [x] Add bot `/leaderboard` command backend integration
- [ ] Build dashboard pages for leaderboard and profile charts

### Changelog

- 2026-04-01: Initial roadmap README created.
- 2026-04-01: Added Phase 0 progress snapshot and updated tracker to reflect current codebase status.
- 2026-04-02: Updated status to reflect completed Phase 1/1.5 and in-progress Phase 2 implementation, including solve verification and streak logic.
- 2026-04-02: Completed remaining Phase 2 hardening (mocked verify endpoint tests, bot command module wiring, backend error mapping).
- 2026-04-02: Started Phase 3 MVP with follow-up question generation and bonus XP answer flow.
- 2026-04-02: Started Phase 4 with cached leaderboard and analytics time-series API endpoints.

## 15) Suggested Milestone Branch Strategy

- `main`: stable milestones only
- `phase-0-foundation`
- `phase-1-integration`
- `phase-1.5-lc-company-track`
- `phase-2-progress-engine`
- `phase-3-followup`
- `phase-4-analytics`
- `phase-5-dashboard`
- `phase-6-prod-readiness`

## 16) Immediate Next Step (What We Should Build Next)

Complete Phase 2 in this order:
Phase 2 is complete.

Move to Phase 3 in this order:
1. Add `followup_questions` and `followup_attempts` models + migration.
2. Build follow-up generation/selection service using problem tags and difficulty.
3. Add endpoint for follow-up answer validation with bonus XP awarding.
4. Wire Discord follow-up command flow.

After these are complete, move directly to Phase 3 (follow-up question engine).
