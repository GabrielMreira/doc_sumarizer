from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from database import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, index=True)
    original_name = Column(String, nullable=False)
    storage_path = Column(String, unique=True, nullable=False)
    doc_entities = Column(JSONB)
    key_words = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InvertedIndexTerm(Base):
    __tablename__ = "inverded_index_term"

    term = Column(String, primary_key=True, index=True)
    doc_id = Column(JSONB, nullable=False)