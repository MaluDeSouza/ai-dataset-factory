from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID, uuid4

class Chunk(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    content: str
    token_count: int
    embedding: Optional[List[float]] = None

class Document(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    dataset_id: UUID
    filename: str
    original_content: Optional[str] = None
    cleaned_content: Optional[str] = None
    category: Optional[str] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # AJUSTE: Propriedade chunks adicionada para o pipeline de fatiamento
    chunks: List[Chunk] = Field(default_factory=list)

class Dataset(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # AJUSTE: default_factory=list previne warnings do Pydantic sobre mutabilidade
    documents: List[Document] = Field(default_factory=list)


class ValidationReport(BaseModel):
    """
    Representa o relatório consolidado de validação e qualidade do dataset.
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    dataset_id: UUID
    total_chunks: int
    valid_chunks: int
    invalid_chunks: int
    summary: str
    details: Optional[str] = None 
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ExportArtifact(BaseModel):
    """
    Representa o ativo físico gerado pela exportação (ex: arquivo JSONL).
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    dataset_id: UUID
    filename: str
    file_path: str
    format: str  
    created_at: datetime = Field(default_factory=datetime.utcnow)