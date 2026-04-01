from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.models.user import User
from app.models.user_platform_stat import UserPlatformStat
from app.schemas.analytics import PlatformAnalyticsResponse

router = APIRouter()


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
