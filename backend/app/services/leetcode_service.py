from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.problem import Problem


def import_leetcode_problems(db: Session, problems: list[dict]) -> tuple[int, int]:
    inserted = 0
    updated = 0
    now = datetime.now(timezone.utc)

    for item in problems:
        slug = item.get("slug")
        if not slug:
            continue

        existing = (
            db.query(Problem)
            .filter(Problem.platform == "leetcode", Problem.lc_slug == slug)
            .one_or_none()
        )

        payload_tags = list(item.get("tags") or [])
        difficulty = item.get("difficulty")
        if difficulty and "difficulty" not in payload_tags:
            payload_tags.append(f"difficulty:{str(difficulty).lower()}")

        if existing:
            existing.name = item.get("name", existing.name)
            existing.url = item.get("url", existing.url)
            existing.tags = payload_tags
            existing.companies = list(item.get("companies") or [])
            existing.lc_problem_id = item.get("problem_id")
            existing.source_last_seen_at = now
            updated += 1
        else:
            db.add(
                Problem(
                    platform="leetcode",
                    name=item.get("name", slug),
                    url=item.get("url", f"https://leetcode.com/problems/{slug}/"),
                    lc_slug=slug,
                    lc_problem_id=item.get("problem_id"),
                    tags=payload_tags,
                    companies=list(item.get("companies") or []),
                    source_last_seen_at=now,
                )
            )
            inserted += 1

    db.commit()
    return inserted, updated
