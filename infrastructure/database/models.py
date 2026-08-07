import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, UUID
from sqlalchemy.dialects.postgresql import ARRAY, FLOAT
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class DatasetModel(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


    documents = relationship("DocumentModel", back_populates="dataset", cascade="all, delete-orphan")
    validation_reports = relationship("ValidationReportModel", back_populates="dataset", cascade="all, delete-orphan")
    export_artifacts = relationship("ExportArtifactModel", back_populates="dataset", cascade="all, delete-orphan")


class DocumentModel(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_content = Column(Text, nullable=True)
    cleaned_content = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    status = Column(String, default="pending", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

   
    dataset = relationship("DatasetModel", back_populates="documents")
    chunks = relationship("ChunkModel", back_populates="document", cascade="all, delete-orphan")


class ChunkModel(Base):
    __tablename__ = "chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    embedding = Column(ARRAY(FLOAT), nullable=True)

    
    document = relationship("DocumentModel", back_populates="chunks")


class ValidationReportModel(Base):
    __tablename__ = "validation_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    total_chunks = Column(Integer, nullable=False)
    valid_chunks = Column(Integer, nullable=False)
    invalid_chunks = Column(Integer, nullable=False)
    summary = Column(Text, nullable=False)
    details = Column(Text, nullable=True)  
    created_at = Column(DateTime, default=datetime.utcnow)

    
    dataset = relationship("DatasetModel", back_populates="validation_reports")


class ExportArtifactModel(Base):
    __tablename__ = "export_artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    format = Column(String, nullable=False)  # Ex: "jsonl", "csv"
    created_at = Column(DateTime, default=datetime.utcnow)

    
    dataset = relationship("DatasetModel", back_populates="export_artifacts")