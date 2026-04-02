from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base


class UserPlatformStat(Base):
    __tablename__ = "user_platform_stats"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    platform = Column(String(20), primary_key=True)

    solved_count = Column(Integer, nullable=False, default=0)
    streak = Column(Integer, nullable=False, default=0)
    last_solved_at = Column(DateTime(timezone=True), nullable=True)

    xp = Column(Integer, nullable=False, default=0)
    rating = Column(Integer, nullable=True)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
