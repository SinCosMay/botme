import logging
from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import func

from app.core.cache import set_cached_json
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.rating_history import RatingHistory
from app.models.user import User
from app.models.xp_history import XpHistory
from app.services.codeforces_service import sync_problemset

logger = logging.getLogger(__name__)

scheduler: AsyncIOScheduler | None = None


def _warm_leaderboard_cache() -> None:
    db = SessionLocal()
    try:
        pages = max(1, settings.SCHEDULER_LEADERBOARD_PAGES)
        limit = max(1, min(settings.SCHEDULER_LEADERBOARD_LIMIT, 100))
        total = db.query(User).count()

        for metric in ("xp", "rating"):
            sort_column = User.xp if metric == "xp" else User.rating
            for page in range(1, pages + 1):
                offset = (page - 1) * limit
                users = db.query(User).order_by(sort_column.desc(), User.id.asc()).offset(offset).limit(limit).all()
                payload = {
                    "metric": metric,
                    "page": page,
                    "limit": limit,
                    "total": total,
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
                        for idx, user in enumerate(users, start=offset + 1)
                    ],
                }
                set_cached_json(f"leaderboard:{metric}:{page}:{limit}", payload, ttl_seconds=120)

        cutoff = datetime.now(timezone.utc) - timedelta(days=max(1, settings.SCHEDULER_TIMESERIES_DAYS))
        top_users = (
            db.query(User)
            .order_by(User.xp.desc(), User.id.asc())
            .limit(max(1, settings.SCHEDULER_TIMESERIES_TOP_USERS))
            .all()
        )
        for user in top_users:
            xp_rows = (
                db.query(func.date(XpHistory.created_at).label("day"), func.sum(XpHistory.amount).label("value"))
                .filter(XpHistory.user_id == user.id, XpHistory.created_at >= cutoff)
                .group_by(func.date(XpHistory.created_at))
                .order_by(func.date(XpHistory.created_at).asc())
                .all()
            )
            xp_payload = {
                "user_id": user.id,
                "metric": "xp",
                "days": settings.SCHEDULER_TIMESERIES_DAYS,
                "points": [{"day": str(row.day), "value": int(row.value or 0)} for row in xp_rows],
            }
            set_cached_json(
                f"timeseries:{user.id}:xp:{settings.SCHEDULER_TIMESERIES_DAYS}",
                xp_payload,
                ttl_seconds=180,
            )

            rating_rows = (
                db.query(func.date(RatingHistory.created_at).label("day"), func.max(RatingHistory.new_rating).label("value"))
                .filter(RatingHistory.user_id == user.id, RatingHistory.created_at >= cutoff)
                .group_by(func.date(RatingHistory.created_at))
                .order_by(func.date(RatingHistory.created_at).asc())
                .all()
            )
            rating_payload = {
                "user_id": user.id,
                "metric": "rating",
                "days": settings.SCHEDULER_TIMESERIES_DAYS,
                "points": [{"day": str(row.day), "value": int(row.value or 0)} for row in rating_rows],
            }
            set_cached_json(
                f"timeseries:{user.id}:rating:{settings.SCHEDULER_TIMESERIES_DAYS}",
                rating_payload,
                ttl_seconds=180,
            )
    except Exception:  # pragma: no cover
        logger.exception("Failed to warm leaderboard cache")
    finally:
        db.close()


async def _sync_codeforces_job() -> None:
    db = SessionLocal()
    try:
        inserted = await sync_problemset(db, limit=settings.CODEFORCES_SYNC_LIMIT)
        logger.info("Codeforces sync completed, inserted=%s", inserted)
    except Exception:  # pragma: no cover
        logger.exception("Codeforces sync job failed")
    finally:
        db.close()


def build_scheduler(*, add_job: Callable[[AsyncIOScheduler], None] | None = None) -> AsyncIOScheduler:
    sched = AsyncIOScheduler(timezone="UTC")
    sched.add_job(
        _warm_leaderboard_cache,
        trigger="interval",
        minutes=max(1, settings.SCHEDULER_CACHE_WARM_MINUTES),
        id="warm_leaderboard_cache",
    )
    if settings.SCHEDULER_ENABLE_CF_SYNC:
        sched.add_job(
            _sync_codeforces_job,
            trigger="interval",
            hours=max(1, settings.SCHEDULER_CF_SYNC_HOURS),
            id="sync_codeforces_problemset",
        )
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
