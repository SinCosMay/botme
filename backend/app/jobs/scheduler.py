import logging
from collections.abc import Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.cache import set_cached_json
from app.core.database import SessionLocal
from app.models.user import User

logger = logging.getLogger(__name__)

scheduler: AsyncIOScheduler | None = None


def _warm_leaderboard_cache() -> None:
    db = SessionLocal()
    try:
        for metric in ("xp", "rating"):
            sort_column = User.xp if metric == "xp" else User.rating
            users = db.query(User).order_by(sort_column.desc(), User.id.asc()).limit(10).all()
            payload = {
                "metric": metric,
                "page": 1,
                "limit": 10,
                "total": db.query(User).count(),
                "entries": [
                    {
                        "rank": idx,
                        "user_id": user.id,
                        "discord_id": user.discord_id,
                        "cf_handle": user.cf_handle,
                        "xp": user.xp,
                        "rating": user.rating,
                        "level": user.level,
                    }
                    for idx, user in enumerate(users, start=1)
                ],
            }
            set_cached_json(f"leaderboard:{metric}:1:10", payload, ttl_seconds=120)
    except Exception:  # pragma: no cover
        logger.exception("Failed to warm leaderboard cache")
    finally:
        db.close()


def build_scheduler(*, add_job: Callable[[AsyncIOScheduler], None] | None = None) -> AsyncIOScheduler:
    sched = AsyncIOScheduler(timezone="UTC")
    sched.add_job(_warm_leaderboard_cache, trigger="interval", minutes=10, id="warm_leaderboard_cache")
    if add_job is not None:
        add_job(sched)
    return sched


def start_scheduler() -> None:
    global scheduler
    if scheduler is not None and scheduler.running:
        return

    scheduler = build_scheduler()
    scheduler.start()
    logger.info("Background scheduler started")


def stop_scheduler() -> None:
    global scheduler
    if scheduler is None:
        return
    if scheduler.running:
        scheduler.shutdown(wait=False)
    scheduler = None
