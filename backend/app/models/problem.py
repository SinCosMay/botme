from uuid import uuid4

from sqlalchemy import Column, Integer, String

from app.core.database import Base


class Problem(Base):
    __tablename__ = "problems"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=True, index=True)
    url = Column(String(500), nullable=False)