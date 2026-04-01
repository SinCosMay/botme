from uuid import uuid4

from sqlalchemy import JSON, Column, ForeignKey, Integer, String

from app.core.database import Base


class FollowupQuestion(Base):
    __tablename__ = "followup_questions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    question_type = Column(String(32), nullable=False)
    prompt = Column(String(1000), nullable=False)
    expected_answer = Column(JSON, nullable=False)
    bonus_xp = Column(Integer, nullable=False, default=10)
