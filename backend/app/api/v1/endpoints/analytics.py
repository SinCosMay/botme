from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.core.cache import get_cached_json, set_cached_json
from app.models.rating_history import RatingHistory
from app.models.xp_history import XpHistory
from app.models.user import User
from app.models.user_platform_stat import UserPlatformStat
from app.schemas.analytics import (
    LeaderboardEntry,
    LeaderboardResponse,
    PlatformAnalyticsResponse,
    TimeSeriesPoint,
    UserTimeSeriesResponse,
)

router = APIRouter()


@router.get("/leaderboard", response_model=LeaderboardResponse)
def leaderboard(
    metric: str = "xp",
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db_session),
) -> LeaderboardResponse:
    metric_key = metric.strip().lower()
    if metric_key not in {"xp", "rating"}:
        raise HTTPException(status_code=400, detail="metric must be xp or rating")
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

    cache_key = f"leaderboard:{metric_key}:{page}:{limit}"
    cached = get_cached_json(cache_key)
    if cached is not None:
        return LeaderboardResponse(**cached)

    sort_column = User.xp if metric_key == "xp" else User.rating
    total = db.query(User).count()
    offset = (page - 1) * limit
    users = (
        db.query(User)
        .order_by(sort_column.desc(), User.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    entries: list[LeaderboardEntry] = []
    for idx, user in enumerate(users, start=offset + 1):
        entries.append(
            LeaderboardEntry(
                rank=idx,
                user_id=user.id,
                discord_id=user.discord_id,
                cf_handle=user.cf_handle,
                xp=user.xp,
                rating=user.rating,
                level=user.level,
            )
        )

    response = LeaderboardResponse(
        metric=metric_key,
        page=page,
        limit=limit,
        total=total,
        entries=entries,
    )
    set_cached_json(cache_key, response.model_dump(), ttl_seconds=60)
    return response


@router.get("/{user_id}", response_model=PlatformAnalyticsResponse)
def user_analytics(
    user_id: str,
    platform: str = "codeforces",
    db: Session = Depends(get_db_session),
) -> PlatformAnalyticsResponse:
    user = db.query(User).filter(User.id == user_id).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    stat = (
        db.query(UserPlatformStat)
        .filter(UserPlatformStat.user_id == user_id, UserPlatformStat.platform == platform)
        .one_or_none()
    )

    if stat is None:
        return PlatformAnalyticsResponse(
            user_id=user_id,
            platform=platform,
            solved_count=0,
            xp=0 if platform == "leetcode" else user.xp,
            rating=None if platform == "leetcode" else user.rating,
            streak=0,
        )

    return PlatformAnalyticsResponse(
        user_id=user_id,
        platform=platform,
        solved_count=stat.solved_count,
        xp=stat.xp,
        rating=stat.rating,
        streak=stat.streak,
    )


@router.get("/{user_id}/timeseries", response_model=UserTimeSeriesResponse)
def user_timeseries(
    user_id: str,
    metric: str = "xp",
    days: int = 30,
    db: Session = Depends(get_db_session),
) -> UserTimeSeriesResponse:
    metric_key = metric.strip().lower()
    if metric_key not in {"xp", "rating"}:
        raise HTTPException(status_code=400, detail="metric must be xp or rating")
    if days < 1 or days > 365:
        raise HTTPException(status_code=400, detail="days must be between 1 and 365")

    user = db.query(User).filter(User.id == user_id).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    cache_key = f"timeseries:{user_id}:{metric_key}:{days}"
    cached = get_cached_json(cache_key)
    if cached is not None:
        return UserTimeSeriesResponse(**cached)

    if metric_key == "xp":
        rows = (
            db.query(func.date(XpHistory.created_at).label("day"), func.sum(XpHistory.amount).label("value"))
            .filter(XpHistory.user_id == user_id)
            .group_by(func.date(XpHistory.created_at))
            .order_by(func.date(XpHistory.created_at).asc())
            .all()
        )
    else:
        rows = (
            db.query(func.date(RatingHistory.created_at).label("day"), func.max(RatingHistory.new_rating).label("value"))
            .filter(RatingHistory.user_id == user_id)
            .group_by(func.date(RatingHistory.created_at))
            .order_by(func.date(RatingHistory.created_at).asc())
            .all()
        )

    points = [TimeSeriesPoint(day=str(row.day), value=int(row.value or 0)) for row in rows]
    response = UserTimeSeriesResponse(
        user_id=user_id,
        metric=metric_key,
        days=days,
        points=points,
    )
    set_cached_json(cache_key, response.model_dump(), ttl_seconds=120)
    return response
