from uuid import uuid4

from sqlalchemy import Column, Integer, String

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    discord_id = Column(String(64), unique=True, nullable=False, index=True)
    cf_handle = Column(String(64), unique=True, nullable=False, index=True)
    xp = Column(Integer, default=0, nullable=False)
    rating = Column(Integer, default=1000, nullable=False)