from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, JSON, String, UniqueConstraint, func

from app.core.database import Base


class Problem(Base):
    __tablename__ = "problems"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    platform = Column(String(20), nullable=False, index=True)  # codeforces|leetcode

    cf_contest_id = Column(Integer, nullable=True)
    cf_index = Column(String(16), nullable=True)

    lc_problem_id = Column(String(64), nullable=True)
    lc_slug = Column(String(255), nullable=True)

    name = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=True, index=True)
    tags = Column(JSON, nullable=False, default=list)
    url = Column(String(500), nullable=False)
    companies = Column(JSON, nullable=True)
    source_last_seen_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("platform", "cf_contest_id", "cf_index", name="uq_problem_cf"),
        UniqueConstraint("platform", "lc_slug", name="uq_problem_lc"),
    )
