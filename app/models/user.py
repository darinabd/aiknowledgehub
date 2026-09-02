from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    password = Column(String, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship(
        "Document",
        back_populates="owner",
        cascade="all, delete-orphan",
    )
