from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint, func

from app.core.database import Base


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    problem_id = Column(String(36), ForeignKey("problems.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(16), nullable=False, default="assigned", index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "problem_id", "status", name="uq_user_problem_assignment_status"),
    )
