from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint, func

from app.core.database import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)

    platform = Column(String(20), nullable=False, index=True)
    cf_submission_id = Column(String(64), unique=True, nullable=True)
    proof_url = Column(String(500), nullable=True)

    verdict = Column(String(32), nullable=False)
    solved_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    xp_awarded = Column(Integer, nullable=False, default=0)
    bonus_xp_awarded = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("user_id", "problem_id", name="uq_user_problem_submission"),
    )
