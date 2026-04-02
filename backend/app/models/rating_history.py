from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base


class RatingHistory(Base):
    __tablename__ = "rating_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    old_rating = Column(Integer, nullable=False)
    new_rating = Column(Integer, nullable=False)
    reason = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
