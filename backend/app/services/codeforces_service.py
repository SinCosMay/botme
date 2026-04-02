from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.problem import Problem


async def verify_handle(cf_handle: str) -> bool:
    if not settings.CODEFORCES_VERIFY_HANDLES:
        return True

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{settings.CODEFORCES_API_BASE}/user.info",
            params={"handles": cf_handle},
        )

    if response.status_code != 200:
        return False

    payload = response.json()
    return payload.get("status") == "OK"


async def sync_problemset(db: Session, limit: int | None = None) -> int:
    resolved_limit = limit or settings.CODEFORCES_SYNC_LIMIT

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{settings.CODEFORCES_API_BASE}/problemset.problems")

    response.raise_for_status()
    payload = response.json()

    if payload.get("status") != "OK":
        raise ValueError("Codeforces API returned non-OK status")

    inserted = 0
    now = datetime.now(timezone.utc)
    for item in payload.get("result", {}).get("problems", [])[:resolved_limit]:
        contest_id = item.get("contestId")
        index = item.get("index")
        if contest_id is None or index is None:
            continue

        existing = (
            db.query(Problem)
            .filter(
                Problem.platform == "codeforces",
                Problem.cf_contest_id == contest_id,
                Problem.cf_index == index,
            )
            .one_or_none()
        )

        url = f"https://codeforces.com/problemset/problem/{contest_id}/{index}"
        if existing:
            existing.name = item.get("name", existing.name)
            existing.rating = item.get("rating")
            existing.tags = item.get("tags", [])
            existing.url = url
            existing.source_last_seen_at = now
        else:
            db.add(
                Problem(
                    platform="codeforces",
                    cf_contest_id=contest_id,
                    cf_index=index,
                    name=item.get("name", f"CF {contest_id}{index}"),
                    rating=item.get("rating"),
                    tags=item.get("tags", []),
                    url=url,
                    source_last_seen_at=now,
                )
            )
            inserted += 1

    db.commit()
    return inserted


async def verify_codeforces_assignment(
    *,
    cf_handle: str,
    contest_id: int,
    index: str,
    assigned_at: datetime,
) -> tuple[bool, str | None]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{settings.CODEFORCES_API_BASE}/user.status",
            params={"handle": cf_handle, "from": 1, "count": 100},
        )

    if response.status_code != 200:
        return False, None

    payload = response.json()
    if payload.get("status") != "OK":
        return False, None

    for sub in payload.get("result", []):
        problem = sub.get("problem", {})
        verdict = sub.get("verdict")
        if problem.get("contestId") != contest_id or problem.get("index") != index:
            continue
        if verdict != "OK":
            continue

        created_seconds = sub.get("creationTimeSeconds")
        if created_seconds is None:
            continue

        created_at = datetime.fromtimestamp(created_seconds, tz=timezone.utc)
        if created_at >= assigned_at.astimezone(timezone.utc):
            return True, str(sub.get("id"))

    return False, None
