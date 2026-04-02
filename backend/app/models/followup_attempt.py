from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base


class FollowupAttempt(Base):
    __tablename__ = "followup_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    submission_id = Column(String(36), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("followup_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_answer = Column(String(2000), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    awarded_xp = Column(Integer, nullable=False, default=0)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
