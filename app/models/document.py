from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base
from app.models.chunk import DocumentChunk


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)
    size = Column(Integer)
    page_count = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="documents")
    text = Column(Text, nullable=True)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
