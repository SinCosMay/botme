from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String, func

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    discord_id = Column(String(64), unique=True, nullable=False, index=True)
    cf_handle = Column(String(64), unique=True, nullable=False, index=True)

    xp = Column(Integer, default=0, nullable=False)
    rating = Column(Integer, default=1000, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)

    last_solved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
