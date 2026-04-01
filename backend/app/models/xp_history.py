from uuid import uuid4

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, func

from app.core.database import Base


class XpHistory(Base):
    __tablename__ = "xp_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Integer, nullable=False)
    source = Column(String(64), nullable=False)
    metadata_json = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
