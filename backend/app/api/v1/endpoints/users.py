from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db_session
from app.models.user import User
from app.schemas.user import UserProfileResponse, UserRegisterRequest
from app.services.codeforces_service import verify_handle

router = APIRouter()


@router.post("/register", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegisterRequest, db: Session = Depends(get_db_session)) -> User:
    existing_discord = db.query(User).filter(User.discord_id == payload.discord_id).one_or_none()
    if existing_discord:
        raise HTTPException(status_code=409, detail="Discord ID already registered")

    existing_cf = db.query(User).filter(User.cf_handle == payload.cf_handle).one_or_none()
    if existing_cf:
        raise HTTPException(status_code=409, detail="Codeforces handle already linked")

    is_valid_handle = await verify_handle(payload.cf_handle)
    if not is_valid_handle:
        raise HTTPException(status_code=400, detail="Invalid Codeforces handle")

    user = User(discord_id=payload.discord_id, cf_handle=payload.cf_handle)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{discord_id}/profile", response_model=UserProfileResponse)
def get_profile(discord_id: str, db: Session = Depends(get_db_session)) -> User:
    user = db.query(User).filter(User.discord_id == discord_id).one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
