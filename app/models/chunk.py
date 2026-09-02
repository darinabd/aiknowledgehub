from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)

    content = Column(Text, nullable=False)

    chunk_index = Column(Integer, nullable=False)

    document_id = Column(
        Integer,
        ForeignKey("documents.id"),
        nullable=False
    )

    document = relationship(
        "Document",
        back_populates="chunks"
    )