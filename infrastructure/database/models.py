import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT

Base = declarative_base()

class DatasetModel(Base):
    __tablename__ = "datasets"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    documents = relationship("DocumentModel", back_populates="dataset", cascade="all, delete-orphan")

class DocumentModel(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    original_content = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    status = Column(String, default="pending")
    
    dataset = relationship("DatasetModel", back_populates="documents")
    chunks = relationship("ChunkModel", back_populates="document", cascade="all, delete-orphan")

class ChunkModel(Base):
    __tablename__ = "chunks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, default=0)
    embedding = Column(ARRAY(FLOAT), nullable=True)
    
    document = relationship("DocumentModel", back_populates="chunks")